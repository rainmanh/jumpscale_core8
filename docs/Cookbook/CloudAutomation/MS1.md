## Mothership 1 Cloud Automation

### preparation

Make sure the portal jumpscale libs are installed
and system redis
```
ays install -n portal_lib
ays install -n redis -i system --data 'param.password: param.port:9999 param.disk:0  param.mem:100 unixsocket:0'

```

```
param.disk                     = @ASK default:0 descr:'REDIS: backup redis to disk as append only default 0 (disabled), 1 (enable)'
param.mem                      = @ASK default:100 descr:'REDIS: Max MEMORY in (MBS)'
param.passwd                   = @ASK type:str descr:'REDIS: password'
param.port                     = @ASK default:9999 descr:'REDIS: port'
param.unixsocket 
```