# Getting Your Feet Wet

- [JumpScale Interactive Shell](JShell.md)
- [Tools] (Tools.md)
- [System Abstraction Layer](SAL.md)
- [Cuisine](Cuisine.md)
- [AtYourService](AYS.md)

@TODO repurpose the below




## SSH key management

SSH is used a lot when using the JumpScale framework. It's used do all remote system manangement, all interactions with GitHub, and more.

In case you don't have SSH keys yet, you can create them using the JumpScale interactive shell, and immediattelly load then into the SSH Agent:

```shell
js 'j.do._.loadSSHAgent(createkeys=True,keyname="despiegk")'
```

In the above command you will of course want to replace the keyname with something that is meaningfull to you.

This single command will do the following for you:

```
- Check if you have `$homedir/.ssh/id_rsa` or `$homedir/.ssh/$keyname` key available
- If an existing key was found, it will be loaded into SSH Agent
- If not, a new one will first get created
```

As part of the SSH creation process you will be asked to enter a passphrase, which should be something that is private to you, and easy to remember.

As a result of the SSH key creation process the public key will be saved as `$homedir/.ssh/id_rsa.pub` or `$homedir/.ssh/$keyname`. This is the key you will have to register at GitHub.

Alternativelly you can also type:

```shell
js 'j.do._.loadSSHAgent()'
```

This will start the SSH Agent if required and load all the keys it can find in `$homedir/.ssh`

You only will need to do this once on a system. Once done the `.bashrc` file will make sure that in every new terminal you have access to your keys.

Remark: if this is the first time then your current session does not have access to sshkeys yet, go into a new terminal to see the results & start using ssh

If you want to read more about key management see [tips & tricks about ssh keys & agents (e.g. how to create your keys)](../SSHSystemManagement/SSHKeysAgent.md)
