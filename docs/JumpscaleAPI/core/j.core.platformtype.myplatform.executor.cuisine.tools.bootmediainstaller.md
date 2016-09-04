<!-- toc -->
## j.core.platformtype.myplatform.executor.cuisine.tools.bootmediainstaller

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/tools/CuisineBootMediaInstaller.py

### Methods

#### arch(*platform='rpi_2b', deviceid*) 

```
if platform none then it will use self._cuisine.node.hwplatform

example: hwplatform = rpi_2b, orangepi_plus,amd64

```

#### debian(*platform='orangepi_plus', deviceid*) 

```
if platform none then it will use self._cuisine.node.hwplatform

example: hwplatform = rpi_2b, orangepi_plus,amd64

```

#### formatCardDeployImage(*url, deviceid, part_type='msdos', post_install*) 

```
will only work if 1 or more sd cards found of 4 or 8 or 16 or 32 GB, be careful will
    overwrite the card
executor = a linux machine

executor=j.tools.executor.getSSHBased(addr="192.168.0.23",
    port=22,login="root",passwd="rooter",pushkey="ovh_install")
executor.cuisine.bootmediaInstaller.formatCards()

:param url: Image url
:param deviceid: Install on this device id, if not provided, will detect all devices that
    are 8,16,or 32GB
:param post_install: A method that will be called with the deviceid before the unmounting
    of the device.

```

#### g8os(*gid, nid, platform='amd64', deviceid, url*) 

```
if platform none then it will use self._cuisine.node.hwplatform

example: hwplatform = rpi_2b, orangepi_plus,amd64

```

#### g8os_arm(*url, gid, nid, deviceid*) 

#### ubuntu(*platform='amd64', deviceid*) 

```
if platform none then it will use self._cuisine.node.hwplatform

example: hwplatform = rpi_2b, orangepi_plus,amd64

```

