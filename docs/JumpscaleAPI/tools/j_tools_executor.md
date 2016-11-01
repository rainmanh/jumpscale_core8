<!-- toc -->
## j.tools.executor

- /opt/jumpscale8/lib/JumpScale/tools/executor/ExecutorFactory.py

### Methods

#### get(*executor='localhost'*) 

```
@param executor is an executor object, None or $hostname:$port or $ipaddr:$port or
    $hostname or $ipaddr

```

#### getJSAgentBased(*agentControllerClientKey, debug, checkok*) 

#### getLocal(*jumpscale, debug, checkok*) 

#### getSSHBased(*addr='localhost', port=22, login='root', passwd, debug, allow_agent=True, look_for_keys=True, timeout=5, usecache=True, passphrase*) 

```
returns an ssh-based executor where:
allow_agent: uses the ssh-agent to connect
look_for_keys: will iterate over keys loaded on the ssh-agent and try to use them to
    authenticate
pushkey: authorizes itself on remote
pubkey: uses this particular key (path) to connect
usecache: gets cached executor if available. False to get a new one.

```

#### getSSHViaProxy(*jumphost, jmphostuser, host, username, port, identityfile, proxycommand*) 

```
To get an executor to host through a jumphost *knows about*.

@param  jumphost is the host we connect through
@param jmphostuser is the user at the jumphost
@host is the host we connect to through the jumphost
@username is the username on host

local> ssh jmphostuser@jumphost
jmphostuser@jumphost> ssh user@host
user@host>

example:
In [1]: ex=j.tools.executor.getSSHViaProxy("192.168.21.163", "cloudscalers",
    "192.168.21.156","cloudscalers", 22, "/home/ahmed/.ssh/id_rsa")

In [2]: ex.cuisine.core.run("hostname")
[Tue06 14:22] - ...mpScale/tools/executor/ExecutorSSH.py:114  - DEBUG    - cmd: hostname
[Tue06 14:22] - ...mpScale/tools/executor/ExecutorSSH.py:128  - INFO     - EXECUTE :22:
    hostname
vm-6

```

#### pushkey(*addr, passwd, keyname='', pubkey='', port=22, login='root'*) 

```
@param keyname is name of key (pub)
@param pubkey is the content of the pub key

```

#### reset(*executor*) 

```
reset remove the executor passed in argument from the cache.

```

