# SSH Basic Connection Tool using Cuisine

## Connect using an SSH agent

```bash
executor = j.tools.executor.getSSHBased(addr='localhost', port=22)

#to test connection
executor.execute("ls /")

Out[2]: 
(2,
 'bin\nboot\nbootstrap.py\ncdrom\ndev\netc\nhome\ninitrd.img\ninitrd.img.old\nlib\nlib64\nlost+found\nmedia\nmnt\nopt\nproc\nroot\nrun\nsbin\nsrv\nsys\ntmp\nusr\nvar\nvmlinuz\nvmlinuz.old\n\n',
 '')
```

## Connect using username and password

```bash
executor=j.tools.executor.getSSHBased(addr='localhost', port=22, login="root", passwd="1234")
```

## Connect using local SSH private key

```bash
executor=j.tools.executor.getSSHBased(addr='localhost', port=22, login="root", passwd="1234", pushkey="ovh_install")
```

## Connect using ssh-agent

```bash
cl=j.clients.ssh.get(addr='remote', login='root', port=22, timeout=10)
```

The ssh-agent will know which agents to use and also remember passphrases of the keys so we don't have to provide them in code.

```
!!!
title = "SSHBasics"
date = "2017-04-08"
tags = ["howto"]
```
