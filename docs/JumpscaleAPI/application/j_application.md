<!-- toc -->
## j.application

- /opt/jumpscale8/lib/JumpScale/core/main/Application.py
- Properties
    - sandbox
    - agentid
    - state
    - gridInitialized
    - noremote
    - jid
    - logger
    - appname
    - skipTraceback
    - interactive

### Methods

#### break_into_jshell(*msg='DEBUG NOW'*) 

#### existAppInstanceHRD(*name, instance, domain='jumpscale'*) 

```
returns hrd for specific appname & instance name (default domain=jumpscale or not used
    when inside a config git repo)

```

#### fixlocale() 

#### getAgentId() 

#### getAppHRDInstanceNames(*name, domain='jumpscale'*) 

```
returns hrd instance names for specific appname (default domain=jumpscale)

```

#### getAppInstanceHRD(*name, instance, domain='jumpscale', parent*) 

```
returns hrd for specific domain,name and & instance name

```

#### getAppInstanceHRDs(*name, domain='jumpscale'*) 

```
returns list of hrd instances for specified app

```

#### getCPUUsage() 

```
try to get cpu usage, if it doesn't work will return 0
By default 0 for windows

```

#### getMemoryUsage() 

```
try to get memory usage, if it doesn't work will return 0i
By default 0 for windows

```

#### getUniqueMachineId() 

```
will look for network interface and return a hash calculated from lowest mac address from
    all physical nics

```

#### getWhoAmiStr() 

#### init() 

#### initGrid() 

#### reload() 

#### reset() 

```
empties the core.db

```

#### start(*name, appdir='.'*) 

```
Start the application

You can only stop the application with return code 0 by calling
j.application.stop(). Don't call sys.exit yourself, don't try to run
to end-of-script, I will find you anyway!

```

#### stop(*exitcode, stop=True*) 

```
Stop the application cleanly using a given exitcode

@param exitcode: Exit code to use
@type exitcode: number

```

#### useCurrentDirAsHome() 

```
use current directory as home for JumpScale
e.g. /optrw/jumpscale8
there needs to be a env.sh in that dir
will also empty redis

```

