# cuisine.group

The `cuisine.group` module handles group operations

Examples for methods in `group`:

- **check**: Checks if there is a group defined with the given name
```python
cuisine.group.check('root')
```
- **create**: Creates a group with the given name, and optionally given gid
```python
cuisine.group.create('admin')
```
- **ensure**: Ensures that the group with the given name (and optional gid) exists.
  ```python
  cuisine.group.ensure('admin')
  ```
