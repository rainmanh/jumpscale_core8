<!-- toc -->
## j.do.installer

- /opt/jumpscale8/lib/JumpScale/InstallTools.py

### Methods

#### cleanSystem() 

#### develtools() 

#### gitConfig(*name, email*) 

#### installJS(*base='', clean=True, insystem=True, GITHUBUSER='', GITHUBPASSWD='', CODEDIR='', JSGIT='https://github.com/Jumpscale/jumpscale_core8.git', JSBRANCH='master', AYSGIT='https://github.com/Jumpscale/ays_jumpscale8', AYSBRANCH='master', SANDBOX='0', EMAIL='', FULLNAME=''*) 

```
@param insystem means use system packaging system to deploy dependencies like python &
    python packages
@param codedir is the location where the code will be installed, code which get's checked
    out from github
@param base is location of root of JumpScale
@copybinary means copy the binary files (in sandboxed mode) to the location, don't link

JSGIT & AYSGIT allow us to chose other install sources for jumpscale as well as
    AtYourService repo

IMPORTANT: if env var's are set they get priority

```

#### installJSDocs(*ssh=True*) 

#### installpip() 

#### prepare(*SANDBOX, base=''*) 

#### replacesitecustomize() 

#### updateOS() 

#### updateUpgradeUbuntu() 

#### writeenv(*basedir='', insystem, CODEDIR='', vardir='', die=True, SANDBOX*) 


```
!!!
title = "J.do.installer"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.do.installer"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.do.installer"
date = "2017-04-08"
tags = []
```
