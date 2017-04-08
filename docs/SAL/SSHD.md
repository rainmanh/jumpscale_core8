# SSHD

The SSHD SAL helps to manage `~/.authorized_keys` file, allowing you to list, add and remove keys and also helps to disable password logins.

You can Access it as follows:

```python
j.sal.sshd
```

We'll be using it as sshd in what follows:

```python
sshd = j.sal.sshd
```

- Initial settings

```python
In [44]: ls /root/.ssh/
authorized_keys  id_rsa  id_rsa.pub  known_hosts

In [45]: cat /root/.ssh/authorized_keys

In [46]: cat /root/.ssh/id
/root/.ssh/id_rsa      /root/.ssh/id_rsa.pub  

In [46]: cat /root/.ssh/id_rsa.pub
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCUlY0UEUNExAQF/sIw2L2AJEmHj0eTCnSCwg7gYOQDNhrrzD0+HJulD1UTz+zZqiC2nIPWMfWBoEs3i4jDj79fyiGx4pgQJXFwioIqTONlEyvPIY0eCm3eeSaWrK9G0STdlCrrofZzuAL5/SCKiqTEizZe1MqhJT/xs2xpD+hHFIyMIuBl9OOLX2XvFQ6mBB1bq4U1jpemuHk7L/M0m73Na4M2CQWVDUl/CRhNyhI+WlB2i9dwI3RwrtUp98MCAF//cx3xVC4NfHONQmN8j7z/WpsfJIadqOxfnOp5y4kj1EqbtmeKZbYvR2ZtcAibcnWs0/4kNDn723NheG/secHT root@myjs8xenial

In [47]: sshd=j.sal.sshd
In [48]: sshd.
sshd.SSH_AUTHORIZED_KEYS  sshd.commit               sshd.erase
sshd.SSH_ROOT             sshd.deleteKey            sshd.keys
sshd.addKey               sshd.disableNonKeyAccess
```

- Accessing the .SSH directory can be done via `SSH_ROOT` attribute

- Accessing the path of the authorized_keys is done via `SSH_AUTHORIZED_KEYS` attribute

```python

In [48]: sshd.SSH_ROOT
Out[48]: path('/root/.ssh')

In [49]: sshd.SSH_AUTHORIZED_KEYS
Out[49]: path('/root/.ssh/authorized_keys')
```

- Adding and deleting public keys is done via `addKey/deleteKey`

- Note that you need to call `commit` to execute the transactions on the `authorized_keys` file

```python
In [50]: k=j.sal.fs 
j.sal.fs        j.sal.fswalker  

In [50]: k=j.sal.fs.readFile("/root/.ssh/id_rs"
/root/.ssh/id_rsa      /root/.ssh/id_rsa.pub  

In [50]: k=j.sal.fs.readFile("/root/.ssh/id_rsa.pub")

In [51]: !cat /root/.ssh/authorized_keys

In [52]: sshd.addKey(k)

In [53]: sshd.commit()

In [54]: sshd.keys
Out[54]: ['ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCUlY0UEUNExAQF/sIw2L2AJEmHj0eTCnSCwg7gYOQDNhrrzD0+HJulD1UTz+zZqiC2nIPWMfWBoEs3i4jDj79fyiGx4pgQJXFwioIqTONlEyvPIY0eCm3eeSaWrK9G0STdlCrrofZzuAL5/SCKiqTEizZe1MqhJT/xs2xpD+hHFIyMIuBl9OOLX2XvFQ6mBB1bq4U1jpemuHk7L/M0m73Na4M2CQWVDUl/CRhNyhI+WlB2i9dwI3RwrtUp98MCAF//cx3xVC4NfHONQmN8j7z/WpsfJIadqOxfnOp5y4kj1EqbtmeKZbYvR2ZtcAibcnWs0/4kNDn723NheG/secHT root@myjs8xenial']

In [55]: sshd.deleteKey(k)

In [56]: sshd.commit()
```

- The `keys` property is used to list the keys in authorized keys

```python
In [58]: sshd.keys  
Out[58]: []

In [59]: cat /root/.ssh/authorized_keys
```

- Erase all public keys from the list of authorized keys

```python
sshd.erase()
```

- Disabling password login, done by adding `PasswordAuthentication no` to your `/etc/ssh/sshd_config`

```python
sshd.disableNonKeyAccess()
```

```
!!!
title = "SSHD"
date = "2017-04-08"
tags = []
```
