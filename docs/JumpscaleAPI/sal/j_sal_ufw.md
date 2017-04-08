<!-- toc -->
## j.sal.ufw

- /opt/jumpscale8/lib/JumpScale/sal/ufw/UFWManager.py

### Methods

#### addRule(*action, source='any', destination='any'*) 

```
Add a new UFW rule

:action: One of the actions defined
    ACTION_ALLOW_IN
    ACTION_ALLOW_OUT
    ACTION_DENY_IN
    ACTION_DENY_OUT
    ACTION_REJECT_IN
    ACTION_REJECT_OUT

:source: Source to match, default to 'any'. Examples of valid sources
    '192.168.1.0/24 proto tcp'
    '22/tcp'
    'any'
    'any on eth0'

:destination: Destination to match, default to 'any'.

```

#### commit() 

```
Apply all bending actions

:example:
    ufw.enabled = False
    ufw.reset()
    ufw.addRule(ufw.ACTION_ALLOW_IN, 'any', '22/tcp')
    ufw.enabled = True

    ufw.commit()

```

#### portClose(*port*) 

```
Short cut to closing a port (which is previously open by portOpen)

```

#### portOpen(*port*) 

```
Short cut to open port

```

#### removeRule(*rule*) 

```
Remove the specified rule

:rule: rule to remove

```

#### reset() 

```
Remove all rules.

```


```
!!!
title = "J Sal Ufw"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Sal Ufw"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Sal Ufw"
date = "2017-04-08"
tags = []
```
