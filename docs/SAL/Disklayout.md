# Disklayout

`j.sal.disklayout` helps you to gather a lot of information about the disks and partitions.

- List of all available disks on machine

```python
j.sal.disklayout.getDisks()
```

## Disk API

- Each disk holds the following attributes:

  - `disk.partitions`: lists of partitions on that disk
  - `disk.name`: device name (ex: /dev/sda)
  - `disk.size`: disk size in bytes
  - `disk.type`: type of disk

- Each disk has the following methods:

  - `disk.erase(force=True)` cleans up the disk by by deleting all non protected partitions and if force=True, deletes all partitions included protected
  - `disk.format(size, hrd)` creates new partition and formats it as configured in the HRD file

  **Note**: the HRD file must contain the following:

  ```
  filesystem                     = '<fs-type>'
  mountpath                      = '<mount-path>'
  protected                      = 0 or 1
  type                           = data or root or tmp
  ```

Example:

```
disk = j.sal.disklayout.getDisks()[0]
disk.paritions
disk.name
disk.size
disk.type
disk.erase(force=True)
disk.format(size, hrd)
```

## Partition API

Each disk has a list of attached partitions. The only way to create a new partition is to call `disk.format()` as explained above.

Each partition holds the following attributes:

- `partition.name`: device name (ex: /dev/sda1)
- `partition.size`: partition size in bytes
- `partition.fstype`: file system type
- `partition.uuid`: file system UUID
- `partition.mountpoint`: get the mount point of partition
- `partition.hrd`: HRD instance used when creating the partition or None
- `partition.delete(force=False)`: deletes the partition and deletes protected partitions if force = True
- `partition.format()`: formats the partition according to HRD
- `partition.mount()`: mounts partition to mountpath defined in HRD
- `partition.setAutoMount(options='defaults', _dump=0, _pass=0)`: which configures partition auto mount `fstab` on `mountpath` defined in HRD
- `partition.unsetAutoMount()`: remotes partition from fstab

partition.hrd can be `None`, in that case partition is considered `unmanaged` which means partition is not created by the SAL. This type of partitions is considered 'protected' by default.

Partition attributes reflects the **real** state of the partition. For example, `mountpoint` will be set if the partition is actually mounted, and is not related to the `mountpath` defined in the HRD file.

Example:

```
disk = j.sal.disklayout.getDisks()[0]
partition = disk.partitions[0]
partition.name
partition.size
partition.fstype
partition.uuid
partition.mountpoint
partition.hrd
partition.delete(force=False)
partition.mount()
partition.format()
partition.setAutoMount(options='defaults', _dump=0, _pass=0)
partition.unsetAutoMount()
```

```
!!!
title = "Disklayout"
date = "2017-04-08"
tags = []
```
