# Getting Started

## JumpScale interactive shell

The best place to get acquainted is in the JumpScale interactive shell, based on IPython.

In order to start the JumpScale interactive shell type `js` at the command line.

Everything after `js` will be evalled in the JumpScale interactive shell session:

```
js 'j.do.loadSSHAgent()'
```

## Installing JumpScale applications

In order to install JumpScale applications there is At Your Service, abbreviated as AYS.

AYS is part of JumpScale. It provides a framework for deploying any application or service so that the application or service becomes self-healing.

To get acquanted with [AYS](/../AtYourService/AtYourService.html) type the following at the command line:

```
ays
```

## SSH key management 

SSH is used a lot when using the JumpScale framework. It's used do all remote system manangement, all interactions with GitHub, and more.

In case you don't have ssh keys yet, you can create them using the JumpScale interactive shell, and immediattelly load then into the SSH Agent:

```shell
js 'j.do.loadSSHAgent(createkeys=True,keyname="despiegk")'
```

In the above command you will of course want to replace the keyname with something that is meaningfull to you.

This single command will do the following for you:
    - Check if you have `$homedir/.ssh/id_rsa` or `$homedir/.ssh/$keyname` key available
    - If an existing key was found, it will be loaded into SSH Agent
    - If not, a new one will first get created

As part of the SSH creation process you will be asked to enter a passphrase, which should be something that is private to you, and easy to remember.

As a result of the SSH key creation process the public key will be saved as `$homedir/.ssh/id_rsa.pub` or `$homedir/.ssh/$keyname`. This is the key you will have to register at GitHub.

Alternativelly you can also type:

```shell
js 'j.do.loadSSHAgent()'
```

This will start the SSH Agent if required and load all the keys it can find in ```$homedir/.ssh```

You only will need to do this once on a system. Once done the `.bashrc` file will make sure that in every new terminal you have access to your keys.

Remark: if this is the first time then your current session does not have access to sshkeys yet, go into a new terminal to see the results & start using ssh

If you want to read more about key management see [tips & tricks about ssh keys & agents (e.g. how to create your keys)](../SSHSystemManagement/SSHKeysAgent.md)


## Some handy shortcuts  

```
#configure git & make sure ssh-agent is configured & ready to go
jscode init

#to go to ssh based login for git do, if you want login/passwd use login=... see help of method
#inside j shell run: 
j.do.changeLoginPasswdGitRepos()

#pull git repo with jumpscale docs, feel free to contribute
j.do.installer.installJSDocs()
```

## Also see

* [IPythonTricks](IPythonTricks.md)
