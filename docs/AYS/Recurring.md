## AYS Recurring

### Manipulate on service object

```
aysi = j.atyourservice.getServiceFromKey("datacenter!palmlab")
aysi.recurring.add(...)
```

```python
def add(name, period, last=0):
  @param 
      name is name of method to do recurring
  @period  
      only supported now is 3m, 3d and 3h (ofcourse 3 can be any int)
      and an int which are seconds
      needs to be at least 5 seconds
```

### service.hrd

```python

recurring.monitor = 1m
recurring.export = 1d
```

is recurring.$actionMethodName = period (see above)

this file is stored in template/directory

### recurring.md

is the file which will be stored in ays directory and has info about what is recurring and what last run was.

