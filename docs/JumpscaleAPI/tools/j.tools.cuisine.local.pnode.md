<!-- toc -->
## j.tools.cuisine.local.pnode

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/CuisinePNode.py
- Properties
    - defaultArch

### Methods

#### buildArchImage(**) 

#### buildG8OSImage(**) 

#### erase(*keepRoot=True*) 

```
if keepRoot == True:
    find boot/root/swap partitions and leave them untouched (check if mirror, leave too)
clean/remove all (other) disks/partitions

```

#### exportRoot(*source='/', destination='/image.tar.gz', excludes=['\\.pyc', '__pycache__']*) 

```
Create an archive of a remote file system
@param excludes is list of regex matches not to include while doing export

```

#### exportRootStor(*storspace, plistname, source='/', excludes=['\\.pyc', '__pycache__'], removetmpdir=True*) 

```
reason to do this is that we will use this to then make the step to g8os with g8osfs (will
    be very small step then)

```

#### formatStorage(*keepRoot=True, mountpoint='/storage'*) 

```
use btrfs to format/mount the disks
use metadata & data in raid1 (if at least 2 disk)
make sure they are in fstab so survices reboot

```

#### importRoot(*source='/image.tar.gz', destination='/'*) 

```
Import and extract an archive to the filesystem

```

#### installArch(*rootsize=5*) 

```
install arch on $rootsize GB root partition

```

#### installG8OS(*rootsize=5*) 

```
install g8os on $rootsize GB root partition

```

