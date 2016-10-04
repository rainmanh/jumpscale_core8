# KVM

The KVM SAL helps to manage kvm elements

You can Access it as follows:

```python
j.sal.kvm
```

It consists of a group of classes to handle creation of virtual machines:

## `j.sal.kvm.KVMController`

This is the controller that will be used by all other classes to manage objects on a given host.

It takes an executor as an argument and it uses it to connect to the host and uses the info of the host to establesh a qemu connection over ssh.

```py
ex = j.tools.executor.getLocal()
co = j.sal.kvm.KVMController(ex)
```

## `j.sal.kvm.Machine`

This is the class for manipulating a virtual machine.

### It takes the following arguments:

```
@param contrller object(j.sal.kvm.KVMController()): controller object to use.
@param name str: machine name
@param disks [object(j.sal.kvm.Disk())]: list of disk instances to be used with machine.
@param nics [object(j.sal.kvm.interface())]: instance of networks to be used with machine.
@param memory int: disk memory in Mb.
@param cpucount int: number of cpus to use.
@param cloud_init bool: option to use cloud_init passing creating and passing ssh_keys,
 user name and passwd to the image
```

### It has the following methods:

#### create

```
Create and define the instanse of the machine xml onto libvirt.

@param username  str: set the username to be set in the machine on boot.
@param passwd str: set the passwd to be set in the machine on boot.
```

#### delete

```
Undefeine machine in libvirt.
```

#### start

```
Start machine.
```

#### stop

```
Shutdown machine.
@param force bool: option force stop a machine (defaults to False)
```

#### suspend == pause

```
Suspend machine, similar to hibernate.
```

#### resume

```
Resume machine if suspended.
```

#### to_xml

```
Return libvirt's xml string representation of the machine.
```

#### create_snapshot

```
Create snapshot of the machine, both disk and ram when reverted will continue as if
    suspended on this state.

@param name str:   name of the snapshot.
@param descrition str: descitption of the snapshot.
```

#### list_snapshots

```
List snapshots of the current machine, if libvirt is true libvirt objects will be returned
else the sal wrapper will be returned.

@param libvirt bool: option to return libvirt snapshot obj or the sal wrapper.
```

#### load_snapshot

```
Revert to snapshot name.

@param name str: name of the snapshot to revert to.
```

### It has the following class methods:


#### from_xml

```
Instantiate a Machine object using the provided xml source and kvm controller object.

@param controller object(j.sal.kvm.KVMController): controller object to use.
@param source  str: xml string of machine.
```

#### get_by_name 

```
Get machine by name passing the controller to search with.

@param controller object(j.sal.kvm.KVMController): controller object to use.
@param name str: name of the machine
```

### It has the following properties:


#### ip

```
Get the ip of the machine
```

#### cuisine

```
Get a cuisine object to the machine (only if created using cloud_init=True)
```

#### state

```
Get a string representing the state of the machine

The available states are:

nostate
running
blocked
paused
shutdown
shutoff
crashed
pmsuspended
last
```

#### domain

```
Get a the domain object represented by python libvirt module
```

## `j.sal.kvm.CloudMachine`

This is a class that inherot from Machine to make creation of a machine easier. It has the same methods and properties in the Machine object.

### It takes the following arguments:

```
@param contrller object(j.sal.kvm.KVMController()): controller object to use.
@param name str: machine name.
@param os str: os name to use.
@param disks int: no of disk names to be used with machine.
@param nics [str]: name of networks to be used with machine.
@param memory int: disk memory in Mb.
@param cpucount int: number of cpus to use.
@param cloud_init bool: option to use cloud_init passing creating and passing ssh_keys, user name and passwd to
the image
```

## `j.sal.kvm.Pool`

This is the class for manipulating a Virtual pool.

### It takes the following arguments:

```
@param contrller object(j.sal.kvm.KVMController()): controller object to use.
@param name str: pool name
```

### It has the following methods:

#### create

```
Create and define the instanse of the pool xml onto libvirt.
```

#### to_xml

```
Return libvirt's xml string representation of the pool.
```

## `j.sal.kvm.Network`

This is the class for manipulating a Virtual pool.

### It takes the following arguments:

```
@param controller object: connection to libvirt controller.
@param name string: name of network.
@param bridge string: bridge name.
@param interfaces list: interfaces list.
```

### It has the following methods:

#### create

```
Create and define the instanse of the network xml onto libvirt.

@param start bool: will start the network after creating it
@param autostart bool: will autostart Network on host boot
create and start network
```

#### destroy

```
Destroy and undefine the network.
```

#### to_xml

```
Return libvirt's xml string representation of the network.
```

### It has the following class methods:


#### from_xml

```
Instantiate a Netowrk object using the provided xml source and kvm controller object.

@param controller object(j.sal.kvm.KVMController): controller object to use.
@param source  str: xml string of network.
```

### It has the following properties:


#### interfaces

```
Get a list of interfaces connected to the network
```

## `j.sal.kvm.Interface`

This is the class for manipulating a virtual interface.

### It takes the following arguments:

```
@param controller object(j.sal.kvm.KVMController()): controller object to use.
@param name str: name of interface
@param mac str: mac address to be assigned to port
@param interface_rate int: qos interface rate to bound to in Kb
@param burst str: maximum allowed burst that can be reached in Kb/s
```

### It has the following methods:

#### to_xml

```
Return libvirt's xml string representation of the interface.
```

#### qos

```
Limit the throughtput into an interface as a for of qos.

@interface str: name of interface to limit rate on
@qos int: rate to be limited to in Kb
@burst int: maximum allowed burst that can be reached in Kb/s
```

### It has the following class methods:


#### from_xml

```
Instantiate an Interface object using the provided xml source and kvm controller object.

@param controller object(j.sal.kvm.KVMController): controller object to use.
@param source  str: xml string of interface.
```

### It has the following properties:


#### ip

```
Get the ip that is assigned to the interface
```

## `j.sal.kvm.Disk`

This is the class for manipulating a virtual Disk.

### It takes the following arguments:

```
@param controller object(j.sal.kvm.KVMController()): controller object to use.
@param pool str: name of the pool to add disk to.
@param name str: name of the disk.
@param size int: size of disk in Mb.
@param image_name  str: name of image to load on disk  if available.
@param disk_iops int: total throughput limit in bytes per second.
```

### It has the following methods:

#### create

```
Create and define the instanse of the disk xml onto libvirt.
```

#### delete

```
delete the instanse of the disk.
```

#### to_xml

```
Return libvirt's xml string representation of the disk.
```

### It has the following class methods:


#### from_xml

```
Instantiate a Disk object using the provided xml source and kvm controller object.

@param controller object(j.sal.kvm.KVMController): controller object to use.
@param source  str: xml string of disk.
```

### It has the following properties:


#### ip

```
Get the ip that is assigned to the interface
```
