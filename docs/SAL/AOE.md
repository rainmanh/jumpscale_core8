# AOE
```
j.sal.aoe.
```
##This library enables the user to do the followig:
* Create a new vDisk.
```
j.sal.aoe.create(storpath, size)
```
* Expose a given storage(vDisk or image path) on a major(shelf):minor(slot) and a certain interface.
```
j.sal.aoe.expose(storage, major, minor, interface)
```
* Unexpose and delete a storage.
```
j.sal.aoe.unexpose(storage)
j.sal.aoe.delete(path)
```
* List all vDisks under a certain location.
```
j.sal.aoe.list(storpath)
```
