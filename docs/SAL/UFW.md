# UFW

```python
j.sal.ufw
```

## This library allows the user to configure the uncomplicated firewall(UFW) by doing the following:

- Enabling and disabling the firewall

```python
j.sal.ufw.enabled(value)
```

- Getting the current status of the firewall

```python
j.sal.ufw.enabled()
```

- Adding, removing and listing firewal rules

```python
j.sal.ufw.addRule(action, source, destination)
j.sal.ufw.removeRule(rule)
j.sal.ufw.rules()
```

- These are the supported actions:

  - ACTION_ALLOW_IN
  - ACTION_ALLOW_OUT
  - ACTION_DENY_IN
  - ACTION_DENY_OUT
  - ACTION_REJECT_IN
  - ACTION_REJECT_OUT

- Resetting the firewall by deleting all the rules

```python
j.sal.ufw.reset()
```

- Opening and closing ports

```python
j.sal.ufw.portOpen(port)
j.sal.ufw.portClose(port)
```

The `commit`method must be called to apply all pending changes to the firwall:

```python
j.sal.ufw.commit()
```

```
!!!
title = "UFW"
date = "2017-04-08"
tags = []
```
