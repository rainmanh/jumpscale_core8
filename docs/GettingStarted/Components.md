## Components

JumpScale consists of the following main components:

* Core
* AYS Service Manager
* Cuisine
* SALs


### Core

This component includes a set of tools and utilities that are not specific to any kind of services, they are rather more general purpose tools.

One of this tools for instance is the **ByteProcessor** module that provides a set of functions to compress/decompress data bytes.

To compress a simple string using blosc compression:

```python
from JumpScale.ExtraTools import ByteProcessor
input = bytearray()
input.extend(map(ord, 'hello jumpscale'))
output = ByteProcessor.compress(input)
ByteProcessor.decompress(output)
```

Other compression algorithms are also avialable:

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


### AYS Service Manager

AYS Service Manager (`ays`) is a standalone command line tool that comes with JumpScale.

It provides a full featured application/service management tool that can install, configure and control a service based on a service configuration template.

For more information in AYS check the section about [AYS](../AYS/AYS-Introduction.md) in this documentation.


### Cuisine

Cuisine makes it easy to automate server installations and create configuration recipes by wrapping common administrative tasks, such as installing packages and creating users and groups, in Python functions.

For more information in Cuisine check the section about [Cuisine](../Cuisine/Cuisine.md) in this documentation.


### SALs

SALs are system abstraction layers. They provide a unified interface to system operations. You can use the different avialable SALs to create powerfull scripts that can monitor and mangae your services.

Goto the section about [SAL](../SAL/SAL.md) in this documentation for more details.

