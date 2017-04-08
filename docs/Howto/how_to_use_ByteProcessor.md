# How to Use ByteProcessor


To compress a simple string using blosc compression:

```python
from JumpScale.ExtraTools import ByteProcessor
input = bytearray()
input.extend(map(ord, 'hello jumpscale'))
output = ByteProcessor.compress(input)
ByteProcessor.decompress(output)
```

Other compression algorithms are also available:

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

- compress/decompess: blosc compression (ultra fast,+ 250MB/sec)
- hashTiger... : ultra reliable hashing (faster than MD5 & longer keys)
- disperse/undiserpse: erasure coding (uses zfec: <https://pypi.python.org/pypi/zfec>)

```
!!!
title = "How To Use ByteProcessor"
date = "2017-04-08"
tags = ["howto"]
```
