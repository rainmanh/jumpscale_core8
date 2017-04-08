<!-- toc -->
## j.tools.objectinspector

- /opt/jumpscale8/lib/JumpScale/tools/objectinspector/ObjectInspector.py
- Properties
    - visited
    - jstree
    - errors
    - dest
    - base
    - classDocs
    - root
    - logger
    - manager
    - apiFileLocation

### Methods

functionality to inspect object structure and generate apifile
and pickled ordereddict for codecompletion

#### generateDocs(*dest, ignore, objpath='j'*) 

```
Generates documentation of objpath in destination direcotry dest
@param dest: destination directory to write documentation.
@param objpath: object path
@param ignore: modules list to be ignored during the import.

```

#### importAllLibs(*ignore, base='/opt/jumpscale8//lib/JumpScale/'*) 

#### inspect(*objectLocationPath='j', recursive=True, parent, obj*) 

```
walk over objects in memory and create code completion api in jumpscale cfgDir under
    codecompletionapi
@param object is start object
@param objectLocationPath is full location name in object tree e.g. j.sal.fs , no need to
    fill in

```

#### raiseError(*errormsg*) 

#### writeDocs(*path*) 

```
Writes the documentation on a specified path.

```


```
!!!
title = "J Tools Objectinspector"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Tools Objectinspector"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Tools Objectinspector"
date = "2017-04-08"
tags = []
```
