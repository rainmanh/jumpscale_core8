<!-- toc -->
## j.sal.diskmanager

- /opt/jumpscale8/lib/JumpScale/sal/diskmanager/Diskmanager.py

### Methods

#### diskGetFreeRegions(*disk, align*) 

```
Get a filtered list of free regions, excluding the gaps due to partition alignment

```

#### mirrorsFind() 

#### partitionAdd(*disk, free, align, length, fs_type, type*) 

```
Add a partition on a disk

```

#### partitionsFind(*mounted, ttype, ssd, prefix='sd', minsize=5, maxsize=5000, devbusy, initialize, forceinitialize*) 

```
looks for disks which are know to be data disks & are formatted ext4

@param ttype is a string variable defining the format type
@param minsize is an int variable indicating the minimum partition size and defaulted to 5
@param mazsize is an int variable indicating the minimum partition size and defaulted to
    5000
@param ssd if None then ssd and other
:return [[$partpath,$size,$free,$ssd]]

```

#### partitionsFind_Ext4Data() 

```
looks for disks which are know to be data disks & are formatted ext4
return [[$partpath,$gid,$partid,$size,$free]]

```

#### partitionsGetMounted_Ext4Data() 

```
find disks which are mounted
@return [[$partid,$size,$free]]

```

#### partitionsMount_Ext4Data() 

#### partitionsUnmount_Ext4Data() 

