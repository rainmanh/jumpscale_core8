<!-- toc -->
## j.data.types.ipport

- /opt/jumpscale8/lib/JumpScale/data/types/CustomTypes.py
- Properties
    - BASETYPE
    - NAME

### Methods

Generic IP port type

#### check(*value*) 

```
Check if the value is a valid port
We just check if the value a single port or a range
Values must be between 0 and 65535

```

#### checkString(*s*) 

#### clean(*value*) 

```
used to change the value to a predefined standard for this type

```

#### fromString(*s*) 

#### get_default(**) 

#### toString(*value*) 

