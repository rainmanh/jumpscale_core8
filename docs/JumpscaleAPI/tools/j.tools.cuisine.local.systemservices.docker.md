<!-- toc -->
## j.tools.cuisine.local.systemservices.docker

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/systemservices/CuisineDocker.py

### Methods

#### dockerStart(*name='ubuntu1', image='jumpscale/ubuntu1604_all', ports='', volumes, pubkey, weave*) 

```
will return dockerCuisineObj: is again a cuisine obj on which all kinds of actions can be
    executed

@param ports e.g. 2022,2023
@param volumes e.g. format: "/var/insidemachine:/var/inhost # /var/1:/var/1
@param ports e.g. format "22:8022 80:8080"  the first arg e.g. 22 is the port in the
    container
@param weave If weave is available on node, weave will be used by default. To make sure
    weave is available, set to True

```

#### getDocker(*name*) 

#### install(*reset*) 

#### isInstalled(**) 

```
Checks if a package is installed or not
You can ovveride it to use another way for checking

```

#### resetPasswd(*dockerCuisineObject*) 

#### ubuntuBuild(*push*) 

