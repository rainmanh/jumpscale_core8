<!-- toc -->
## j.application.config

- /opt/jumpscale8/lib/JumpScale/data/hrd/HRDTree.py
- Properties
    - changed
    - items
    - commentblock
    - path
    - keepformat
    - prefixWithName
    - hrds
    - name

### Methods

#### add2tree(*path, recursive=True*) 

#### add2treeFromContent(*content*) 

#### applyOnContent(*content, additionalArgs*) 

```
look for $(name) and replace with hrd value

```

#### applyOnDir(*path, filter, minmtime, maxmtime, depth, changeFileName=True, changeContent=True, additionalArgs*) 

```
look for $(name) and replace with hrd value

```

#### applyOnFile(*path, additionalArgs*) 

```
look for $(name) and replace with hrd value

```

#### checkValidity(*template, hrddata*) 

```
@param template is example hrd content block, which will be used to check against,
if params not found will be added to existing hrd

```

#### delete(*key*) 

#### exists(*key*) 

#### get(*key, default*) 

#### getBool(*key, default*) 

#### getDict(*key*) 

#### getDictFromPrefix(*prefix*) 

```
returns values from prefix return as list

```

#### getFloat(*key*) 

#### getHRDAsDict() 

#### getHrd(*key*) 

#### getInt(*key, default*) 

#### getList(*key, default*) 

#### getListFromPrefix(*prefix*) 

```
returns values from prefix return as list

```

#### getListFromPrefixEachItemDict(*prefix, musthave, defaults, aredict, arelist, areint, arebool*) 

```
returns values from prefix return as list
each value represents a dict
@param musthave means for each item which is dict, we need to have following keys
@param specifies the defaults
@param aredicts & arelist specifies which types

```

#### getStr(*key, default*) 

#### listAdd(*key, item*) 

#### pop(*key*) 

#### prefix(*key, depth*) 

```
@param depth means prefix level to return

```

#### prefixexists(*key*) 

#### processall() 

#### set(*key, val, persistent=True*) 


```
!!!
title = "J Application Config"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Application Config"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Application Config"
date = "2017-04-08"
tags = []
```
