<!-- toc -->
## j.tools.cuisine.local.development.pip

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/development/CuisinePIP.py

### Methods

#### ensure() 

#### install(*package, upgrade*) 

```
The "package" argument, defines the name of the package that will be installed.

```

#### multiInstall(*packagelist, upgrade*) 

```
@param packagelist is text file and each line is name of package
can also be list

e.g.
    # influxdb
    # ipdb
    # ipython
    # ipython-genutils
    itsdangerous
    Jinja2
    # marisa-trie
    MarkupSafe
    mimeparse
    mongoengine

@param runid, if specified actions will be used to execute

```

#### packageRemove(*package*) 

```
The "package" argument, defines the name of the package that will be ensured.
The argument "r" referes to the requirements file that will be used by pip and
is equivalent to the "-r" parameter of pip.
Either "package" or "r" needs to be provided

```

#### packageUpgrade(*package*) 

```
The "package" argument, defines the name of the package that will be upgraded.

```


```
!!!
title = "J Tools Cuisine Local Development Pip"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Tools Cuisine Local Development Pip"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Tools Cuisine Local Development Pip"
date = "2017-04-08"
tags = []
```
