> WORK IN PROGRESS


If everything went smooth, test your installation by starting a `js` and then do the following

```python
j.clients.agentcontroller.get(address='localhost', port=6379, password=None)
```

This should return something like

```python
{u'hostname': u'b0cadd75e49c',
 u'os': u'linux',
 u'platform': u'ubuntu',
 u'platform_family': u'debian',
 u'platform_version': u'14.04',
 u'procs': 0,
 u'uptime': 1436087357,
 u'virtualization_role': u'',
 u'virtualization_system': u''}
```

> Client provides some shortcut methods for ease of access.

# Using the clients and runArgs

You can execute any command on the agent using the client low level method `cmd`

```python
def cmd(self, gid, nid, cmd, args, data=None, id=None):
        """
        Executes a command, return a cmd descriptor
        :gid: grid id
        :nid: node id
        :cmd: one of the supported commands (execute, execute_js_py, get_?_info, etc...)
        :args: instance of RunArgs
        :data: Raw data to send to the command standard input. Passed as objecte and will be dumped as json on wire
        :id: id of command for retrieve later, if None a random GUID will be generated.
        """
```

## CMD Arguments

- `gid` Grid ID
- `nid` Node ID
- `cmd` can be one of (execute, execute_js_py, get_os_info, get_disk_info, etc...)
- `args` are the run arguments and must be instance of `RunArgs`. you can get `args` like

  ```python
  runargs = j.clients.agentcontroller.runArgs(domain='jumpscale', name='ls', args=['-l', '/opt'])
  ```

- `data` Optional data is passed to the executed command over `stdin`

- `id` Optional id to identify the command, if None a random guid will be generated

# Examples

## Starting nginx (long running process)

```python
args = j.clients.agentcontroller.getRunArgs(domain='js', name='nginx', args=['-c', '/etc/nginx/nginx.conf'], max_time=-1)
client = j.clients.agentcontroller.get(password='<redis-password>')

cmd = client.cmd(gid, nid, 'execute', args)

#Same can be approached by doing the following
args = j.clients.agentcontroller.getRunArgs(domain='js', max_time=-1)
client = j.clients.agentcontroller.get(password='<redis-password>')

cmd = client.execute(gid, nid, 'nginx', ['-c', '/etc/nginx/nginx.conf'], args)
```

This will immediately start nginx on agent.

> For long running process (the jobs that doesn't return results) we should implement a way to get start status (either it started or not)

## Running a job that returns data

Agent can also run short running jobs that do some action and optionally returns a result. Jobs that produces output must follow the specs on how output is returned from the script

> Jobs must format the `result` as a log message of one of the levels [20-23]

```python
cmd = client.execute(1, 1, 'ls', ['-l', '/root'])
job = cmd.get_next_result()

#Result will look like that
{u'args': {u'args': [u'-l', u'/opt'],
  u'loglevels': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 20, 21, 22, 23, 30],
  u'name': u'ls',
  u'stats_interval': 60},
 u'cmd': u'execute',
 u'data': u'',
 u'gid': 1,
 u'id': u'5525c8df-b3aa-4a6a-bdfe-0ac0259f8a59',
 u'level': 0,
 u'nid': 1,
 u'starttime': 1437026653101,
 u'state': u'SUCCESS',
 u'time': 212}
```

returned results represents the `execution` results, the `result['data']` should hold the job output. But why it's empty in this case? Simply because ls doesn't output the results in the correct format! it doesn't put it's result in the correct message format expected.

To work around this we can simply rerun the command as following

```python
cmd = client.execute(1, 1, 'bash', ['-c', 'echo 20::: && ls -l /opt && echo :::'])
job = cmd.get_next_result()

#then
print job.data
```

will output

```raw
total 0
drwxr-xr-x 1 root root  20 Jul 15 12:40 build
drwxr-xr-x 1 root root  18 Jul 15 11:51 code
drwxr-xr-x 1 root root  48 Jul 15 11:56 influxdb
drwxr-xr-x 1 root root 118 Jul 16 06:04 jumpscale7
drwxr-xr-x 1 root root   6 Jul 15 11:55 mongodb
drwxr-xr-x 1 root root 144 Jul 15 11:59 nginx
drwxr-xr-x 1 root root  94 Jul 15 12:00 nodejs
drwxr-xr-x 1 root root 442 Jul 15 12:00 statsd-collector
drwxr-xr-x 1 root root 436 Jul 15 12:00 statsd-master
```

An alternative approach would be enabling stdout capturing by setting `loglevels_db` `runargs`

```python
args = j.clients.agentcontroller.getRunArgs(loglevels_db='1')
cmd = client.execute(1, 1, 'bash', ['-c', 'ls -l /opt'], args=args)
job = cmd.get_next_result()
print job.state # should be SUCCESS
msgs = job.get_msgs(limit=100) # default limit is set to 20
for msg in msgs[::-1]:  # logs are ordered from new to old
    print msg['data']
```

> Note: `get_next_result()` will block for the available result with optional timeout (default to zero which means wait forever). The next call on get_next_result() will block until another result is ready. This is useful in case the job is `faneout` or runs on multiple agents.

> Note: `cmd` also provides a `get_jobs()` method that will not block for results, instead will return a dict with all the (available) job results where the keys are tuples `(<gid>, <nid>)`.

# Adding custom execute cmd to Agent

According to [[agent configuration]] you can add custom execution commands to execute arbitrary scripts.

```bash
vi /opt/jumpscale8/apps/agent2/agent2.toml
```

You can find this under the `extensions` secion

```toml
[extensions.execute_js_py]
binary = "python2.7"
cwd = "/opt/scripts"
```

It basically tells the agent that the `execute_js_py` command will Run the python2.7 /opt/scripts/

<args[name]>
</args[name]>

To test this add a python file under `/opt/scripts/`

```python
#file test.py



data = {'name': 'Test script'}
print '20:::'
print j.data.serializer.json.dumps(data)
print ':::'
```

Running the command

```python
cmd = client.cmd(1, 1, 'execute_js_py', j.clients.agentcontroller.getRunArgs(name='test.py'))
```
