# Disklayout

`j.sal.disklayout` helps you to gather many information about the disks and partitions.

* List of all available disks on machine.
```
j.sal.disklayout.getDisks()
```
### Disk API
* Each disk holds the following attributes:
  - `disk.partitions`: lists of partitions on that disk
  - `disk.name`: device name (ex: /dev/sda)
  - `disk.size`: disk size in bytes
  - `disk.type`: type of disk
* Each disk has the following methods: 
  - `disk.erase(force=True)`: which clean up the disk by by deleting all non protected partitions and if force=True, delete ALL partitions included protected
  - `disk.format(size, hrd)`: which creates new partition and format it as configured in hrd file

    Note:
    hrd file must contain the following
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
### Partition API

Each disk has a list of attached partitions. The only way to create a new partition is to call `disk.format()` as explained above.

Each partition holds the following attributes

- `partition.name`: device name (ex: /dev/sda1)
- `partition.size`: partition size in bytes
- `partition.fstype`: filesystem 
- `partition.uuid`: filesystem UUID
- `partition.mountpoint`: get the mount point of partition
- `partition.hrd`: HRD instance used when creating the partition or None 
- `partition.delete(force=False)`: deletes the partition and deletes protected partitions if force = True
- `partition.format()`: formats the partition according to HRD
- `partition.mount()`: mounts partition to mountpath defined in HRD
- `partition.setAutoMount(options='defaults', _dump=0, _pass=0)`: which configures partition auto mount `fstab` on `mountpath` defined in HRD
- `partition.unsetAutoMount()`: remote partition from fstab

partition.hrd can be `None`, in that case partition is considered `unmanaged` Which means partition is NOT created by the SAL. This type of partitions is considered 'protected' by default

Partition attributes reflects the **real** state of the partition. For example, `mountpoint` will be set IF the partition is actually mounted, and is not related to the `mountpath` defined in the hrd file.

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
