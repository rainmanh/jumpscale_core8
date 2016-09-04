<!-- toc -->
## j.tools.cuisine.local.processmanager

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/CuisineProcessManager.py
- Properties
    - logger

### Methods

#### ensure(*name, cmd, env, path='', descr='', systemdunit='', **kwargs*) 

```
Ensures that the given systemd service is self._cuisine.core.running, starting
it if necessary and also create it
@param systemdunit is the content of the file, will still try to replace the cmd

```

#### exists(*name*) 

#### get(*pm*) 

#### list(*prefix=''*) 

```
@return [$name]

```

#### reload(**) 

#### remove(*prefix*) 

#### restart(**) 

#### start(*name*) 

#### stop(*name*) 

