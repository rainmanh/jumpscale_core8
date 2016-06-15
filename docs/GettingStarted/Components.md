# Components

JumpScale consists of the following main components:

* Core
* AYS Service Manager
* SALs

## Core

This component includes a set of tools and utilities that are not specific to any kind of services but more general purpose tools.

### An examples: ByteProcessor

The ByteProcessor module provide a set of functions to compress/decompress data bytes.

To compress a simple string using blosc compression:

```python
from JumpScale.ExtraTools import ByteProcessor
input = bytearray()
input.extend(map(ord, 'hello jumpscale'))
output = ByteProcessor.compress(input)
ByteProcessor.decompress(output)
```

Other compression algorithms are also avialable

```python
from JumpScale.ExtraTools import ByteProcessor
ByteProcessor.compress                 
ByteProcessor.disperse                 
ByteProcessor.hashMd5                  
ByteProcessor.hashTiger192             
ByteProcessor.decompress               
ByteProcessor.getDispersedBlockObject  
ByteProcessor.hashTiger160             
ByteProcessor.undisperse
```

-   compress/decompess: blosc compression (ultra fast,+ 250MB/sec)
-   hashTiger... : ultra reliable hashing (faster than MD5 & longer keys)
-   disperse/undiserpse: erasure coding (uses zfec: <https://pypi.python.org/pypi/zfec>)

## AYS Service Manager

AYS Service Manager (`ays`) is a standalone command line tool that comes with JumpScale. It provides a full featured application/service management tool that can install, configure and control a service based on a service configuration template.

## SALs

SALs are system abstraction layers. They provide a unified interface to system operations. You can use the different avialable SALs to create powerfull scripts that can monitor and mangae your services.

The following is some useful SALs that can be used, but more can be found under j.sal.[tab]
* [Docker](../SAL/Docker.md)
* [Disk Layout](../SAL/Disklayout.md)
* [SSHD](../SAL/SSHD.md)
* [FS](../SAL/FS.md)

### How to add a new SAL

1- Switch to the SAL directory

```cd jumpscale_core8/lib/JumpScale/sal```/

2- Create a package directory

```mkdir hello```

3- Create the package files

```touch Hello.py __init__.py```

4- Edit Hello.py
Each SAL object is required to extend the base SALObject class
SAL modules must have a name that starts with capital letter to be loaded (`Hello.py` not `hello.py`)
```python
from JumpScale import j

class Hello:

    def __init__(self):
        self.__jslocation__ = 'j.sal.hello'
        self.logger = j.logger.get('j.sal.hello')
        self.msg=''
        
    def message(self, msg):
        self.msg = msg
    
    def upper(self):
        return self.msg.upper()

    def lower(self):
        return self.msg.lower()

    def manytimes(self, n):
        return (self.msg + " ")*n + "!!!"

```
5- You will need to execute `j.core.db.flushall()/j.core.db.flushdb()` in order to force it to reread the SALs directory

6- (Re)start the `js` session

7- Use it:
```
In [1]: j.sal.hello.upper()
Out[1]: ''

In [2]: j.sal.hello.message('hello')

In [3]: j.sal.hello.manytimes(3)
Out[3]: 'hello hello hello !!!'

```
