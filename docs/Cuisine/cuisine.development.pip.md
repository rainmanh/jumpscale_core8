# cuisine.development.pip

The `cuisine.development.pip` module is for Python package management.

Examples for methods in `pip`:

- **install**: to install a Python package

  ```python
  cuisine.development.pip.install('pygments')
  ```

- **multiInstall**: for installing multiple Python packages; the packages are passed as a newline separated string, with a hash at the beginning of the packages to be skipped

  ```python
  cuisine.development.pip.multiInstall("""flask
  pygments""")
  ```

- **remove**: to remove a package

  ```python
  cuisine.development.pip.remove('pygments')
  ```

- **upgrade**: to upgrade a package

  ```python
  cuisine.development.pip.packageUpgrade('pygments')
  ```
