<!-- toc -->
## j.tools.path

- /opt/jumpscale8/lib/JumpScale/tools/path/PathFactory.py

### Methods

#### get(*startpath*) 

```
example1:
```
d = j.tools.path.get("/tmp")
for i in d.walk():
    if i.isfile():
        if i.name.startswith("something_"):
            i.remove()
```

other:
files = d.walkfiles("*.pyc")
num_files = len(d.files())

```


```
!!!
title = "J.tools.path"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.tools.path"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.tools.path"
date = "2017-04-08"
tags = []
```
