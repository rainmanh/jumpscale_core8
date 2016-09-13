<!-- toc -->
## j.data.types

- /opt/jumpscale8/lib/JumpScale/data/types/Types.py
- Properties
    - yaml
    - path
    - json
    - guid
    - date
    - string
    - float
    - duration
    - tel
    - ipaddr
    - ipport
    - list
    - email
    - iprange
    - dict
    - multiline
    - bytes
    - set
    - bool
    - int

### Methods

#### get(*ttype, val*) 

```
type is one of following
- str, string
- int, integer
- float
- tel, mobile
- ipaddr, ipaddress
- ipport, tcpport
- iprange
- email
- multiline
- list
- dict
- set
- guid
- duration e.g. 1w, 1d, 1h, 1m, 1

```

#### getTypeClass(*ttype*) 

```
type is one of following
- str, string
- int, integer
- float
- bool,boolean
- tel, mobile
- ipaddr, ipaddress
- ipport, tcpport
- iprange
- email
- multiline
- list
- dict
- yaml
- set
- guid
- duration e.g. 1w, 1d, 1h, 1m, 1

```

