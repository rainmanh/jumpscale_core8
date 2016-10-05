<!-- toc -->
## j.tools.cuisine.local.systemservices.kvm

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/systemservices/CuisineKVM.py

### Methods

usage:

```
c=j.tools.cuisine.get("ovh4")
c.systemservices.kvm.install()
```

#### download_image(*url, overwrite*) 

#### get_machine_by_name(*name*) 

#### iamgeGetPath(*name*) 

#### install() 

#### machineCreate(*name, os='xenial-server-cloudimg-amd64-uefi1.img', disks=[10], nics=['vms1'], memory=2000, cpucount=4, cloud_init=True, start=True, resetPassword=True*) 

```
@param disks is array of disk names (after using diskCreate)
@param nics is array of nic names (after using nicCreate)

will return kvmCuisineObj: is again a cuisine obj on which all kinds of actions can be
    executed

@param pubkey is the key which will be used to get access to this kvm, if none then use
    the std ssh key as used for docker

```

#### poolCreate(*name*) 

#### vdiskBootCreate(*name, image='http://fs.aydo.com/kvm/ub_small.img'*) 

#### vdiskCreate(*pool, name, size=100, image_name=''*) 

```
create an empty disk we can attachl
@param size in GB

```

#### vdiskDelete(*name*) 

#### vdisksList() 

#### vmGetPath(*name*) 

#### vmachinesList() 

#### vpoolCreate(*name*) 

#### vpoolDestroy(*name*) 

