## UFW

```py
j.sal.ufw
```

### This library allows the user to configure the uncomplicated firewall(UFW) by doing the following:

* Enabling and disabling the firewall

```py
j.sal.ufw.enabled(value)
```

* Getting the current status of the firewall

```py
j.sal.ufw.enabled()
```

* Adding, removing and listing firewal rules

```py
j.sal.ufw.addRule(action, source, destination)
j.sal.ufw.removeRule(rule)
j.sal.ufw.rules()
```

* These are the supported actions:
  * ACTION_ALLOW_IN
  * ACTION_ALLOW_OUT
  * ACTION_DENY_IN
  * ACTION_DENY_OUT
  * ACTION_REJECT_IN
  * ACTION_REJECT_OUT
 
* Resetting the firewall by deleting all the rules

```py
j.sal.ufw.reset()
```

* Opening and closing ports

```py
j.sal.ufw.portOpen(port)
j.sal.ufw.portClose(port)
```

The `commit`method must be called to apply all pending changes to the firwall:

```py
j.sal.ufw.commit()
```