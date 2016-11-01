<!-- toc -->
## j.tools.cuisine.local.systemservices.openvswitch

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/systemservices/CuisineOpenvSwitch.py

### Methods

usage:

```
c=j.tools.cuisine.get("ovh4")
c.systemservices.openvswitch.install()
```

#### install() 

#### isInstalled() 

```
Checks if a package is installed or not
You can ovveride it to use another way for checking

```

#### networkCreate(*network_name, bridge_name, interfaces*) 

```
Create a network interface using libvirt and open v switch.

@network_name str: name of the network
@bridge_name str: name of the main bridge created to connect to th host
@interfaces [str]: names of the interfaces to be added to the bridge

```

#### networkDelete(*bridge_name*) 

```
Delete network and bridge related to it.

@bridge_name

```

#### networkList() 

```
List bridges available on machaine created by openvswitch.

```

#### networkListInterfaces(*name*) 

```
List ports available on bridge specified.

```

#### vnicBond(*parameter_list*) 

#### vnicCreate(*name, bridge*) 

```
Create and interface and relevant ports connected to certain bridge or network.

@name  str: name of the interface and port that will be creates
@bridge str: name of bridge to add the interface to
@qos int: limit the allowed rate to be used by interface

```

#### vnicDelete(*name, bridge*) 

```
Delete interface and port related to certain machine.

@bridge str: name of bridge
@name str: name of port and interface to be deleted

```

#### vnicQOS(*name, bridge, qos, burst*) 

```
Limit the throughtput into an interface as a for of qos.

@interface str: name of interface to limit rate on
@qos int: rate to be limited to in Kb
@burst int: maximum allowed burst that can be reached in Kb/s

```

