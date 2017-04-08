# SSH Agent Tips

```bash
#load ssh-agent & all known keys
js 'j.do._.loadSSHAgent()'

#if it's the first time you need to tell current session path to ssh-agent
export SSH_AUTH_SOCK=~/sshagent_socket

#add another private ssh key(s) you require
ssh-add ~/ssh2/id_rsa

#list agent keys
ssh-add -l

#kill my own agents started as above
ssh-agent -k
```

Just add all the keys you require and the ssh-agent will remember them for you.

## Generate keys

```
ssh-keygen -t rsa -b 4096 -C "your_email@example.com -f ~/.ssh/mynewkey"
```

## Authorize remote key

At the CLI:

```bash
#copy your pub key to remote server authorized keys (add at end of file)
scp root@remoteserver.com:/home/despiegk/ssh2/id_rsa.pub /tmp/mykey.pub
ssh root@remoteserver.com cat /tmp/mykey.pub >> /root/.ssh/authorized_keys
```

This will allow youme from yiur local server to login as root on the remote machine.

Using JumpScale:

```python
j.do.SSHAuthorizeKey(remoteipaddr,login="root",passwd=None)
```

If `psswd=None` you will be asked for the password.

## Varia

```bash
#restart
/etc/init.d/ssh restart

#kill all ssh-agents (is dirty)
killall ssh-agent
```

## Secure your sshd config

```bash
#create recovery user (if needed)
adduser recovery

#make sure user is in sudo group
usermod -a -G sudo recovery

#sed -i -e '/texttofind/ s/texttoreplace/newvalue/' /path/to/file
sed -i -e '/.*PermitRootLogin.*/ s/.*/PermitRootLogin without-password/' /etc/ssh/sshd_config
sed -i -e '/.*UsePAM.*/ s/.*/UsePAM no/' /etc/ssh/sshd_config
sed -i -e '/.*Protocol.*/ s/.*/Protocol 2/' /etc/ssh/sshd_config

#only allow root & recovery user (make sure it exists)
sed -i -e '/.*AllowUsers.*/d' /etc/ssh/sshd_config
echo 'AllowUsers root' >> /etc/ssh/sshd_config
echo 'AllowUsers recovery' >> /etc/ssh/sshd_config

/etc/init.d/ssh restart
```

## Allow root to login

Dangerous do not do this, use sudo -s from normal user account""

```bash
sed -i -e '/.*PermitRootLogin.*/ s/.*/PermitRootLogin yes/' /etc/ssh/sshd_config
/etc/init.d/ssh restart
```

```
!!!
title = "SSHKeysAgent"
date = "2017-04-08"
tags = []
```
