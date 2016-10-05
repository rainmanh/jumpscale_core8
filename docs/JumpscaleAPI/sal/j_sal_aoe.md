<!-- toc -->
## j.sal.aoe

- /opt/jumpscale8/lib/JumpScale/sal/aoe/AOEManager.py

### Methods

#### create(*storpath, size=10*) 

```
Create and vdisk

:storpath: is the full image path.
:size: size in GB

```

#### delete(*path*) 

```
Delete path

```

#### expose(*storage, major, minor, inf*) 

```
Expose the given image on major:minor and interface

:storage: the image path or vdisk
:major: Major number (shelf)
:minor: Minor number (slot)
:inf: Network interface

```

#### list(*storpath='/mnt/disktargets/'*) 

```
List all vdisks under this location.
Note that all files in that directory are assumed to be valid images

```

#### unexpose(*storage*) 

```
Unexpose the storage

```

