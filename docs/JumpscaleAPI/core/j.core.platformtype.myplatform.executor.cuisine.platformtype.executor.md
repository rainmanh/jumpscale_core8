<!-- toc -->
## j.core.platformtype.myplatform.executor.cuisine.platformtype.executor

- /opt/jumpscale8/lib/JumpScale/tools/executor/ExecutorLocal.py
- Properties
    - checkok
    - dest_prefixes
    - type
    - debug
    - id
    - curpath
    - logger
    - env
    - jumpscale
    - platformtype
    - addr

### Methods

#### checkplatform(*name*) 

```
check if certain platform is supported
e.g. can do check on unix, or linux, will check all

```

#### docheckok(*cmd, out*) 

#### download(*source, dest, source_prefix=''*) 

#### execute(*cmds, die=True, checkok, async, showout=True, outputStderr, timeout, env*) 

#### executeInteractive(*cmds, die=True, checkok*) 

#### executeRaw(*cmd, die=True, showout*) 

#### exists(*path*) 

#### init(**) 

#### upload(*source, dest, dest_prefix='', recursive=True*) 

