<!-- toc -->
## j.data.types.tel

- /opt/jumpscale8/lib/JumpScale/data/types/CustomTypes.py
- Properties
    - NAME
    - BASETYPE

### Methods

format is e.g. +32 475.99.99.99x123
only requirement is it needs to start with +
the. & , and spaces will not be remembered
and x stands for phone number extension

#### check(*value*) 

```
Check whether provided value is a string

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

