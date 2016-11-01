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

#### pushkey(*addr, passwd, keyname='', pubkey='', port=22, login='root'*) 

```
@param keyname is name of key (pub)
@param pubkey is the content of the pub key

```

#### reset(*executor*) 

```
reset remove the executor passed in argument from the cache.

```

