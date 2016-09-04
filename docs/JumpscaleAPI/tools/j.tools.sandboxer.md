<!-- toc -->
## j.tools.sandboxer

- /opt/jumpscale8/lib/JumpScale/tools/sandboxer/Sandboxer.py
- Properties
    - original_size
    - exclude
    - new_size

### Methods

sandbox any linux app

#### copyTo(*path, dest, excludeFileRegex, excludeDirRegex, excludeFiltersExt=['pyc', 'bak']*) 

#### dedupe(*path, storpath, name, excludeFiltersExt=['pyc', 'bak'], append, reset, removePrefix='', compress=True, delete, excludeDirs*) 

#### findLibs(*path*) 

#### sandboxLibs(*path, dest, recursive*) 

```
find binaries on path and look for supporting libs, copy the libs to dest
default dest = '%s/bin/'%j.dirs.base

```

#### sandbox_python3(**) 

