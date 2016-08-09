# Jumpscripts interface

A jumpscript must define one method `action` that takes data. Data can be any json serializable object. The action can return a json serializable object as well

Let's assume we have this jumpscript wich increments any given number by 1

```python
from JumpScale import j

def action(data):
    # do stuff with the data
    j.logger.log('Received data is: %s' % data)

    result = data + 1
    return result
```

Then place this file under in

```bash
/opt/jumpscale8/apps/AgentController8/jumpscripts/test/incrementer.py
```

(create the `test` folder if needed)

> `test` is the domain name in that case

> Also note that after placing the folder under `AgentController8/jumpscripts` it can take up to a minute until the script is distributed to all agents as descriped per [Scripts Distribution](ScriptsDistribution.md)

# use of std client

# @todo

## use client_advanced

Now to execute your script do the following in a `js` shell. Make sure you have latest AgentController8_client installed:

```python
client =  j.clients.agentcontroller.get()

cmd = client.execute_jumpscript(1, 1, 'test', 'incrementer', data=10)

job = cmd.get_next_result()

#`job` should be like this:

{u'args': {u'domain': u'test',
  u'loglevels': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 20, 21, 22, 23, 30],
  u'name': u'test',
  u'stats_interval': 60},
 u'cmd': u'jumpscript',
 u'data': u'12',
 u'gid': 1,
 u'id': u'ac556dca-ebf6-4494-90f9-4fea16eb9087',
 u'level': 20,
 u'nid': 1,
 u'starttime': 1442320129165,
 u'state': u'SUCCESS',
 u'time': 1058}
```

Note that, `job.data` is the json (`level 20`) serialized return of the JumpScript, to get it's value you can do:

```python
data = j.data.serializer.json.loads(job.data)
```
