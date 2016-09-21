# Disk Manager

`j.sal.diskmanager` is a very helpful SAL to manager your disk.

## Managing your disks

- Get a filtered list of free regions in a disk, excluding the gaps due to partition alignment

```python
j.sal.diskmanager.diskGetFreeRegions(disk, align)
```

- Add a partition on a disk

```python
j.sal.diskmanager.partitionAdd(disk, free, align=None, length=None, fs_type=None, type=None)
```

- Finding partitions

  ```python
  j.sal.diskmanager.partitionsFind(mounted=None,ttype=None,ssd,prefix="sd",minsize=5,maxsize=5000,devbusy=None,initialize=False,forceinitialize=False)
  ```

> `ttype` is a string variable defining the format type

> `minsize` is an int variable indicating the minimum partition size and defaulted to 5

> `mazsize` is an int variable indicating the minimum partition size and defaulted to 5000

- Findings ext4 data disks, and returns `partpath,gid,partid,size,free`

```python
j.sal.diskmanager.partitionsFind_Ext4Data()
```

- Finding mounted ext4 data disks, and returns `partid,size,free`

```python
j.sal.diskmanager.partitionsGetMounted_Ext4Data():
```

- Mounting/unmounting ext4 partitions

```python
j.sal.diskmanager.partitionsMount_Ext4Data()
j.sal.diskmanager.partitionsUnmount_Ext4Data()
```
