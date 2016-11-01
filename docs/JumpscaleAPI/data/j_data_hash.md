<!-- toc -->
## j.data.hash

- /opt/jumpscale8/lib/JumpScale/data/hash/HashTool.py

### Methods

#### blake2(*path*) 

```
Calculate blake2 hash of data available in a file

The file will be opened in read/binary mode and blocks of the blocksize
used by the hashing implementation will be read.

@param path: Path to file to calculate content hash
@type path: string

@returns: blake2 hash of data available in the given file
@rtype: number

```

#### blake2_string(*s*) 

```
Calculate blake2 hash of input string

@param s: String value to hash
@type s: string

@returns: blake2 hash of the input value
@rtype: number

```

#### crc32(*path*) 

```
Calculate CRC32 hash of data available in a file

The file will be opened in read/binary mode and blocks of the blocksize
used by the hashing implementation will be read.

@param path: Path to file to calculate content hash
@type path: string

@returns: CRC32 hash of data available in the given file
@rtype: number

```

#### crc32_string(*s*) 

```
Calculate CRC32 hash of input string

@param s: String value to hash
@type s: string

@returns: CRC32 hash of the input value
@rtype: number

```

#### hashDir(*rootpath*) 

```
walk over all files, calculate md5 and of sorted list also calc md5 this is the resulting
    hash for the dir independant from time and other metadata (appart from path)

```

#### md5(*path*) 

```
Calculate %(alg)s hash of data available in a file

The file will be opened in read/binary mode and blocks of the blocksize
used by the hashing implementation will be read.

@param path: Path to file to calculate content hash
@type path: string

@returns: %(alg)s hash hex digest of data available in the given file
@rtype: string

```

#### md5_string(*s*) 

```
Calculate %(alg)s hash of input string

@param s: String value to hash
@type s: string

@returns: %(alg)s hash hex digest of the input value
@rtype: string

```

#### sha1(*path*) 

```
Calculate %(alg)s hash of data available in a file

The file will be opened in read/binary mode and blocks of the blocksize
used by the hashing implementation will be read.

@param path: Path to file to calculate content hash
@type path: string

@returns: %(alg)s hash hex digest of data available in the given file
@rtype: string

```

#### sha1_string(*s*) 

```
Calculate %(alg)s hash of input string

@param s: String value to hash
@type s: string

@returns: %(alg)s hash hex digest of the input value
@rtype: string

```

#### sha256(*path*) 

```
Calculate %(alg)s hash of data available in a file

The file will be opened in read/binary mode and blocks of the blocksize
used by the hashing implementation will be read.

@param path: Path to file to calculate content hash
@type path: string

@returns: %(alg)s hash hex digest of data available in the given file
@rtype: string

```

#### sha256_string(*s*) 

```
Calculate %(alg)s hash of input string

@param s: String value to hash
@type s: string

@returns: %(alg)s hash hex digest of the input value
@rtype: string

```

#### sha512(*path*) 

```
Calculate %(alg)s hash of data available in a file

The file will be opened in read/binary mode and blocks of the blocksize
used by the hashing implementation will be read.

@param path: Path to file to calculate content hash
@type path: string

@returns: %(alg)s hash hex digest of data available in the given file
@rtype: string

```

#### sha512_string(*s*) 

```
Calculate %(alg)s hash of input string

@param s: String value to hash
@type s: string

@returns: %(alg)s hash hex digest of the input value
@rtype: string

```

