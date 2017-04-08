# Samba

```python
j.sal.samba
```

## This library enables the user to do the following:

- Add, remove, list Samba shares

```python
j.sal.samba.addShare(sharename, path, options)
    # options variable is a dictionary of options
j.sal.samba.removeShare(sharename)
j.sal.samba.listShares()
```

- Add, remove, list Samba subshares

```python
j.sal.samba.addSubShare(sharename, sharepath)
j.sal.samba.removeSubShare(sharename, sharepath)
j.sal.samba.listSubShares(path)
```

- Searches for a share or a subshare with it's name and returns it as an object

```python
j.sal.samba.getShare(sharename)
j.sal.samba.getSubShare(sharename)
```

- Add, remove, list Samba users

```python
j.sal.samba.addUser(username, password)
j.sal.samba.removeUser(username)
j.sal.samba.listUsers()
```

- Granting and Revoking users' access over shares

```python
j.sal.samba.grantaccess(username, sharename, sharepath, readonly)
j.sal.samba.revokeaccess(username, sharename, sharepath, readonly)
    # readonly is a boolean variable
```

The method `commit` must be called to apply all pending changes to shares:

`j.sal.samba.commitShare()`

## Here is an example:

```python
from JumpScale import j
from .manager import Samba

s = j.ssh.samba.get(j.ssh.connect())

print('========================')
print('===   SAMBA SHARES   ===')
print('========================')

print('-> Get')
print(s.getShare('sysvol'))
print(s.getShare('hello'))

print('-> Add')
print(s.addShare('test', '/tmp/'))
print(s.addShare('homes', '/tmp/'))
print(s.addShare('noread', '/tmp/', {'read only': 'true'}))

print('-> Remove')
print(s.removeShare('global'))
print(s.removeShare('notexists'))
print(s.removeShare('test'))

print('-> Commit')
print(s.commitShare())

print('=======================')
print('===   SAMBA USERS   ===')
print('=======================')

print('-> List')
print(s.listUsers())

print('-> Add')
print(s.addUser('test', 'test'))
print(s.addUser('test', 'test@1234xxx'))

print('-> Remove')
print(s.removeUser('test'))
print(s.removeUser('test'))
print(s.removeUser('test2'))
```

```
!!!
title = "Samba"
date = "2017-04-08"
tags = []
```
