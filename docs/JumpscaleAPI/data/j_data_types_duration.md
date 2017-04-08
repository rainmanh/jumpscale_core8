<!-- toc -->
## j.data.types.duration

- /opt/jumpscale8/lib/JumpScale/data/types/CustomTypes.py
- Properties
    - NAME
    - BASETYPE

### Methods

Duration type

Understood formats:
- #w week
- #d days
- #h hours
- #m minutes
- #s seconds

e.g. 10d is 10 days
if int then in seconds

-1 is infinite

#### check(*value*) 

```
Check whether provided value is a string

```

#### clean(*value*) 

```
used to change the value to a predefined standard for this type

```

#### convertToSeconds(*value*) 

```
Translate a string representation of a duration to an int
representing the amount of seconds.

Understood formats:
- #w week
- #d days
- #h hours
- #m minutes
- #s seconds

@param value: number or string representation of a duration in the above format
@type value: string or int
@return: amount of seconds
@rtype: int

```

#### fromString(*s*) 

```
return string from a string (is basically no more than a check)

```

#### get_default() 

#### toString(*v*) 


```
!!!
title = "J Data Types Duration"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Data Types Duration"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Data Types Duration"
date = "2017-04-08"
tags = []
```
