# First Steps

The easiest way to get to know the JumpScale well is to start the IPython interactive shell.

Execute the following command:

```shell
js
```

## Play with the default loaded libraries

You can walk around in the JumpScale namespace by using `j.` and hit the tab key.

## Get info about a method for a JumpScale lib

In the interactive shell type: `j.sal.fs.createDir?`

```python
In [1]: j.sal.fs.createDir(?
File:       /usr/lib/python2.7/JumpScale/core/system/fs.py
Definition: o.system.fs.createDir(self, newdir, skipProtectedDirs=False)
Docstring:
Create new Directory
@param newdir: string (Directory path/name)
if newdir was only given as a directory name, the new directory will be created on the default path,
if newdir was given as a complete path with the directory name, the new directory will be created in the specified path
```

## How to know where a library is on the file system

See above, look at help of method, the _File: ..._ shows where the file is that implements the method.

## How to load extra modules in JumpScale script

Type `JumpScale.` and then hit the tab key:

```python
import JumpScale.[tab]
```

This will show you which libs can be imported.

The only relevant ones for now to start with are:

- JumpScale.baselib: a standard set of quite a lot of base libraries
- JumpScale.grid: the core grid system
- JumpScale.portal: the core portal system

To drill deeper:

```python
import JumpScale.baselib.[tab]
```
