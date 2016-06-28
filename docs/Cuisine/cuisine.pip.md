## cuisine.pip

The `cuisine.pip` module is for Python package management.

Examples for methods in `pip`:

- **install**: to install a Python package
  
  ```py
  cuisine.pip.install('pygments')
  ```

- **multiInstall**: for installing multiple Python packages; the packages are passed as a newline separated string, with a hash at the beginning of the packages to be skipped

  ```py
  cuisine.pip.multiInstall("""flask
  pygments""")
  ```
  
- **remove**: to remove a package

  ```py
  cuisine.pip.remove('pygments')
  ```

- **upgrade**: to upgrade a package
  
  ```py
  cuisine.pip.upgrade('pygments')
  ```