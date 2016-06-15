
# ssh agent tips


```
#load ssh-agent & all known keys
js 'j.do.loadSSHAgent()'

#if its first time need to tell current session path to ssh-agent
export SSH_AUTH_SOCK=~/sshagent_socket

#add another private ssh key(s) you require
ssh-add ~/ssh2/id_rsa

#list agent keys
ssh-add -l

#kill my own agents started as above
ssh-agent -k

```

just add all the keys you require & the sshagent will remember them for you

generate keys
--------------

```
ssh-keygen -t rsa -b 4096 -C "your_email@example.com -f ~/.ssh/mynewkey"
```

authorize remote key
--------------------

bash way
```
#copy your pub key to remote server authorized keys (add at end of file)
scp root@remoteserver.com:/home/despiegk/ssh2/id_rsa.pub /tmp/mykey.pub
ssh root@remoteserver.com cat /tmp/mykey.pub >> /root/.ssh/authorized_keys
```

this will allow me from my local server to login as root on the remote machine

jumpscale way
```
j.do.authorizeSSHKey(remoteipaddr,login="root",passwd=None)
```
if passwd None then will be asked for

varia
-----

```
#restart
/etc/init.d/ssh restart

#kill all ssh-agents (is dirty)
killall ssh-agent

```

secure your sshd config
-----------------------
```
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

allow root to login
-------------------
dangerous do not do this, use sudo -s from normal user account
```
sed -i -e '/.*PermitRootLogin.*/ s/.*/PermitRootLogin yes/' /etc/ssh/sshd_config
/etc/init.d/ssh restart
```



