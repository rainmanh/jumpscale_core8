<!-- toc -->
## j.data.types

- /opt/jumpscale8/lib/JumpScale/data/types/Types.py
- Properties
    - email
    - set
    - guid
    - list
    - string
    - float
    - json
    - bytes
    - path
    - ipaddr
    - tel
    - ipport
    - date
    - dict
    - bool
    - int
    - duration
    - iprange
    - yaml
    - multiline

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

