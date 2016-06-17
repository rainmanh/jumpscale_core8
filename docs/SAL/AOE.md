##AOE

```py
j.sal.aoe.
```

### This library enables the user to do the followig:

* Create a new vDisk

```py
j.sal.aoe.create(storpath, size)
```

* Expose a given storage(vDisk or image path) on a major(shelf):minor(slot) and a certain interface

```py
j.sal.aoe.expose(storage, major, minor, interface)
```

* Unexpose and delete a storage

```py
j.sal.aoe.unexpose(storage)
j.sal.aoe.delete(path)
```

* List all vDisks under a certain location

```py
j.sal.aoe.list(storpath)
```