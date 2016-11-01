<!-- toc -->
## j.tools.xonsh.executor

- /opt/jumpscale8/lib/JumpScale/tools/executor/ExecutorLocal.py
- Properties
    - debug
    - platformtype
    - dest_prefixes
    - id
    - env
    - curpath
    - addr
    - type
    - logger
    - jumpscale
    - checkok

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

#### init() 

#### upload(*source, dest, dest_prefix='', recursive=True*) 

