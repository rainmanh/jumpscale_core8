<!-- toc -->
## j.data.types.date

- /opt/jumpscale8/lib/JumpScale/data/types/CustomTypes.py
- Properties
    - NAME

### Methods

Date
-1 is indefinite in past
0 is now
+1 is indefinite in future
+1d will be converted to 1 day from now, 1 can be any int
+1w will be converted to 1 week from now, 1 can be any int
+1w_end will be converted to 1 week from now at end of week (Saturday), 1 can be any int
+1m_end will be converted to 1 week from now at end of month (last day of month), 1 can be any int

#### check(*value*) 

```
Check whether provided value is a valid tel nr

```

#### clean(*v*) 

```
used to change the value to a predefined standard for this type

```

#### fromString(*s*) 

```
return string from a string (is basically no more than a check)

```

#### get_default() 

#### toString(*v*) 


```
!!!
title = "J.data.types.date"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.data.types.date"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.data.types.date"
date = "2017-04-08"
tags = []
```
