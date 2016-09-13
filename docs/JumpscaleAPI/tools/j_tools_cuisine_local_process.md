<!-- toc -->
## j.tools.cuisine.local.process

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/CuisineProcess.py

### Methods

#### find(*name, exact*) 

```
Returns the pids of processes with the given name. If exact is `False`
it will return the list of all processes that start with the given
`name`.

```

#### info_get(*prefix=''*) 

#### kill(*name, signal=9, exact*) 

```
Kills the given processes with the given name. If exact is `False`
it will return the list of all processes that start with the given
`name`.

```

#### tcpport_check(*port, prefix=''*) 

