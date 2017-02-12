<!-- toc -->
## j.clients.ssh

- /opt/jumpscale8/lib/JumpScale/clients/ssh/SSHClient.py
- Properties
    - logger
    - cache

### Methods

#### close() 

#### get(*addr='', port=22, login='root', passwd, stdout=True, forward_agent=True, allow_agent=True, look_for_keys=True, timeout=5, key_filename, passphrase, die=True, usecache=True*) 

```
gets an ssh client.
@param addr: the server to connect to
@param port: port to connect to
@param login: the username to authenticate as
@param passwd: leave empty if logging in with sshkey
@param stdout: show output
@param foward_agent: fowrward all keys to new connection
@param allow_agent: set to False to disable connecting to the SSH agent
@param look_for_keys: set to False to disable searching for discoverable private key files
    in ~/.ssh/
@param timeout: an optional timeout (in seconds) for the TCP connect
@param key_filename: the filename to try for authentication
@param passphrase: a password to use for unlocking a private key
@param die: die on error
@param usecache: use cached client. False to get a new connection

If password is passed, sshclient will try to authenticated with login/passwd.
If key_filename is passed, it will override look_for_keys and allow_agent and try to
    connect with this key.

```

#### SSHKeyGetFromAgentPub(*keyname='', die=True*) 

#### removeFromCache(*client*) 

#### reset() 

