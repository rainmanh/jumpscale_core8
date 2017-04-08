<!-- toc -->
## j.tools.cuisine.local.systemservices.kvm

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/systemservices/CuisineKVM.py

### Methods

usage:

```
c=j.tools.cuisine.get("ovh4")
c.systemservices.kvm.install()
```

#### diskGetPath(*name*) 

#### install() 

#### machineCreate(*name, disks, nics, mem, pubkey*) 

```
@param disks is array of disk names (after using diskCreate)
@param nics is array of nic names (after using nicCreate)

will return kvmCuisineObj: is again a cuisine obj on which all kinds of actions can be
    executed

@param pubkey is the key which will be used to get access to this kvm, if none then use
    the std ssh key as used for docker

```

#### prepare() 

#### vdiskBootCreate(*name, image='http://fs.aydo.com/kvm/ub_small.img'*) 

#### vdiskCreate(*name, size=100*) 

```
@param size in GB

```

#### vdiskDelete(*name*) 

#### vdiskQOS(*name, **kwargs*) 

```
set vdisk QOS settings at runtime

```

#### vdisksList() 

#### vmGetPath(*name*) 

#### vnicCreate(*name*) 

#### vnicDelete(*name*) 

#### vnicQOS(*name, **kwargs*) 

```
set vnic QOS settings at runtime

```

#### vnicsList(***kwargs*) 


```
!!!
title = "J.tools.cuisine.local.systemservices.kvm"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.tools.cuisine.local.systemservices.kvm"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.tools.cuisine.local.systemservices.kvm"
date = "2017-04-08"
tags = []
```
