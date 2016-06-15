
SSH Basic Connection Tool Using Cusisine (low level)
==========================

connect using an ssh agent
----

```
executor=j.tools.executor.getSSHBased(addr='localhost', port=22)

#to test connection

executor.execute("ls /")

Out[2]: 
(2,
 'bin\nboot\nbootstrap.py\ncdrom\ndev\netc\nhome\ninitrd.img\ninitrd.img.old\nlib\nlib64\nlost+found\nmedia\nmnt\nopt\nproc\nroot\nrun\nsbin\nsrv\nsys\ntmp\nusr\nvar\nvmlinuz\nvmlinuz.old\n\n',
 '')

```


connect using login/passwd
--------------------------

```
executor=j.tools.executor.getSSHBased(addr='localhost', port=22, login="root",passwd="1234")
```

connect using local ssh private key
--------------------------

```
executor=j.tools.executor.getSSHBased(addr='localhost', port=22,login="root",passwd="1234",pushkey="ovh_install")
```

connect using ssh-agent
--------------------------
```
cl=j.clients.ssh.get(addr='remote', login='root', port=22, timeout=10)
```
the ssh-agent will know which agents to use & also remember passphrases of the keys so we don't have to provide them in code

