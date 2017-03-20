---
title: cuisine run: how to use bash profile
tags: jumpscale

## cuisine run: how to use bash profile

many installs set config params in the profile of the machine,
to make sure that they are used when running a command use the profile =True

```python
self.cuisine.core.run("npm config set global true ", profile=True)
```
