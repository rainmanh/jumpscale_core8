# cuisine.btrfs

The `cuisine.btrfs` module handles btrfs operations

Examples for methods in `btrfs`:

- **deviceAdd**: Adds a device to a filesystem.
```python
cuisine.btrfs.deviceAdd('\', device)
```
- **getSpaceUsageDataFree**: Gets free data percentage
```python
cuisine.btrfs.getSpaceUsageDataFree()
```
- **subvolumeExists**: Checks if subvolume exists in the given path

  ```python
  cuisine.btrfs.subvolumeExists('/')
  ```
