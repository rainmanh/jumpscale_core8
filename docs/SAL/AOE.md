# ATA over Ethernet (AoE)

```python
j.sal.aoe.
```

## This library enables the user to do the followig:

- Create a new vDisk

```python
j.sal.aoe.create(storpath, size)
```

- Expose a given storage(vDisk or image path) on a major(shelf):minor(slot) and a certain interface

```python
j.sal.aoe.expose(storage, major, minor, interface)
```

- Unexpose and delete a storage

```python
j.sal.aoe.unexpose(storage)
j.sal.aoe.delete(path)
```

- List all vDisks under a certain location

```python
j.sal.aoe.list(storpath)
```
