# ByteProcessor

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