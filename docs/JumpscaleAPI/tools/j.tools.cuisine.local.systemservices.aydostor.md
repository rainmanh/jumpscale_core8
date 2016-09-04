<!-- toc -->
## j.tools.cuisine.local.systemservices.aydostor

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/systemservices/CuisineAydoStor.py

### Methods

#### build(*addr='0.0.0.0:8090', backend='$varDir/aydostor', start=True, install=True, reset*) 

```
Build and Install aydostore
@input addr, address and port on which the service need to listen. e.g. : 0.0.0.0:8090
@input backend, directory where to save the data push to the store

```

#### install(*addr='0.0.0.0:8090', backend='$varDir/aydostor', start=True*) 

```
download, install, move files to appropriate places, and create relavent configs

```

#### isInstalled(**) 

```
Checks if a package is installed or not
You can ovveride it to use another way for checking

```

#### start(*addr*) 

