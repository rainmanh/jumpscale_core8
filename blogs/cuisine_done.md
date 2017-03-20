---
title: how to avoid repeating an action in cuisine (done function)
tags: jumpscale
---

## how to avoid repeating an action in cuisine (done function)

- typical way how to get something done over cuisine and not do double

```python

j.tools.cuisine.getFromId(" 91.121.132.123")

def hexo(c):
    if c.core.doneGet("install_hexo"):
        return
    cmd = "npm install hexo -cli -g"
    c.core.run(cmd)
    c.core.doneSet("install_hexo")


hexo(c)

```

how does this work?

- most of cuisine base classes have a doneGet/doneSet/doneReset
- there is a config file on the node see

```
In [6]: c.core
Out[6]: cuisine:core:91.121.132.123:22

In [7]: c.core.config
[Mon20 10:36] - ExecutorSSH.py      :231 :j.executorssh91.121.132.123    - DEBUG    - EXECUTE 91.121.132.123:22: uname -mnprs
[Mon20 10:36] - ExecutorSSH.py      :231 :j.executorssh91.121.132.123    - DEBUG    - EXECUTE 91.121.132.123:22: uname -a
[Mon20 10:36] - ExecutorSSH.py      :231 :j.executorssh91.121.132.123    - DEBUG    - EXECUTE 91.121.132.123:22: cat /etc/lsb-release
[Mon20 10:36] - ExecutorSSH.py      :231 :j.executorssh91.121.132.123    - DEBUG    - EXECUTE 91.121.132.123:22: cat /etc/hostname
[Mon20 10:37] - ExecutorSSH.py      :231 :j.executorssh91.121.132.123    - DEBUG    - EXECUTE 91.121.132.123:22: test -e /optvar/jsexecutor.json
[Mon20 10:37] - ExecutorSSH.py      :231 :j.executorssh91.121.132.123    - DEBUG    - EXECUTE 91.121.132.123:22: test -e /optvar/jsexecutor.json
[Mon20 10:37] - ExecutorSSH.py      :231 :j.executorssh91.121.132.123    - DEBUG    - EXECUTE 91.121.132.123:22: cat /optvar/jsexecutor.json | base64
Out[7]:
{'done': {'install_docker': True,
  'install_js': True,
  'storage_mount_done': True}}
```

- this config file is in: /optvar/jsexecutor.json
- this file can be used for anything, configuration info but also to store which actions where done

### more info

- see [[cuisine_config.md]] how to use the config json in cuisine
