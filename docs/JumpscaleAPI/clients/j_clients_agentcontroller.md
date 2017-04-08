<!-- toc -->
## j.clients.agentcontroller

- /opt/jumpscale8/lib/JumpScale/clients/agentcontroller/Client.py

### Methods

#### get(*address='localhost', port=6379, password*) 

#### getAdvanced(*address='localhost', port=6379, password*) 

#### getRunArgs(*domain, name, max_time, max_restart, recurring_period, stats_interval, args, loglevels='*', loglevels_db, loglevels_ac, queue*) 

```
Creates a reusable run arguments object

:domain: Domain name
:name: script or executable name
:max_time: Max run time, 0 (forever), -1 forever but remember during reboots (long
    running),
    other values is timeout
:max_restart: Max number of restarts if process died in under 5 min.
:recurring_period: Scheduling time
:stats_interval: How frequent the stats aggregation is done/flushed to AC
:args: Command line arguments (in case of execute)
:loglevels: Which log levels to capture and pass to logger
:loglevels_db: Which log levels to store in DB (overrides logger defaults)
:loglevels_ac: Which log levels to send to AC (overrides logger defaults)

```


```
!!!
title = "J Clients Agentcontroller"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Clients Agentcontroller"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Clients Agentcontroller"
date = "2017-04-08"
tags = []
```
