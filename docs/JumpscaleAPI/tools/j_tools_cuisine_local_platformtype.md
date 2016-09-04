<!-- toc -->
## j.tools.cuisine.local.platformtype

- /opt/jumpscale8/lib/JumpScale/core/main/PlatformTypes.py
- Properties
    - myplatform
    - executor
    - cache

### Methods

#### checkMatch(*match*) 

```
match is in form of linux64,darwin
if any of the items e.g. darwin is in getMyRelevantPlatforms then return True

```

#### dieIfNotPlatform(*platform*) 

#### has_parent(*name*) 

#### isGeneric() 

```
Checks whether the platform is generic (they all should)

```

#### isHyperV() 

```
Check whether the system supports HyperV

```

#### isLinux() 

```
Checks whether the platform is Linux-based

```

#### isUnix() 

```
Checks whether the platform is Unix-based

```

#### isVirtualBox() 

```
Check whether the system supports VirtualBox

```

#### isWindows() 

```
Checks whether the platform is Windows-based

```

#### isXen() 

```
Checks whether Xen support is enabled

```

