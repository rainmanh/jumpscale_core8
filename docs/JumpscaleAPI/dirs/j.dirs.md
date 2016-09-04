<!-- toc -->
## j.dirs

- /opt/jumpscale8/lib/JumpScale/core/main/Dirs.py
- Properties
    - varDir
    - pidDir
    - hrd
    - tmpDir
    - codeDir
    - homeDir
    - libDir
    - libExtDir
    - appDir
    - jsLibDir
    - base
    - binDir
    - cfgDir
    - logDir
    - tmplsDir

### Methods

Utility class to configure and store all relevant directory paths

#### getPathOfRunningFunction(*function*) 

#### init() 

#### replaceFilesDirVars(*path, recursive=True, filter, additionalArgs*) 

#### replaceTxtDirVars(*txt, additionalArgs*) 

```
replace $base,$vardir,$cfgDir,$bindir,$codedir,$tmpdir,$logdir,$appdir with props of this
    class
also the Dir... get replaces e.g. varDir

```

