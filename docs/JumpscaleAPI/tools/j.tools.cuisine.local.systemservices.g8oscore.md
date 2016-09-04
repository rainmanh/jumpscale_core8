<!-- toc -->
## j.tools.cuisine.local.systemservices.g8oscore

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/systemservices/CuisineG8OSCore.py

### Methods

#### build(*start=True, gid, nid, install=True*) 

```
builds and setsup dependencies of agent to run , given gid and nid
neither can be the int zero, can be ommited if start=False

```

#### install(*start=True, gid, nid*) 

```
download, install, move files to appropriate places, and create relavent configs

```

#### isInstalled(**) 

```
Checks if a package is installed or not
You can ovveride it to use another way for checking

```

#### start(*gid, nid, controller_url='http://127.0.0.1:8966'*) 

```
if this is run on the sam e machine as a controller instance run controller first as the
core will consume the avialable syncthing port and will cause a problem

```

