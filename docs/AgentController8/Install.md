# How to install using atyourservice

```bash
# make sure you have a redis instance installed.
TODO: use new ays commands to install 
ays install -n AgentController8
ays install -n AgentController8_client
ays install -n agent2
```

# How to install manually locally in a jsshell:

```
executor = j.tools.executor.getLocal()
cuisine = j.tools.cuisine.get(executor)
cuisine.apps.controller.build(start=True)
```

## Testing setup

Start a `jumpscale` shell

```python
client = j.clients.agentcontroller.get()
client.get_os_info(1, 1)
```

this should return something like

```python
{u'hostname': u'ea724b563ab8',
 u'os': u'linux',
 u'platform': u'ubuntu',
 u'platform_family': u'debian',
 u'platform_version': u'14.04',
 u'procs': 0,
 u'uptime': 1436087357,
 u'virtualization_role': u'',
 u'virtualization_system': u''}
```

```
!!!
title = "Install"
date = "2017-04-08"
tags = []
```
