Installation
============
## Requirements
- Python 3.5
- curl

Ubuntu
------
Use the installation script to make your life easy.

Note: if you can install it as root, do it, otherwise please use `sudo -s -H`

```shell
sudo -s -H
apt-get update
apt-get -y dist-upgrade
apt-get install -y python3.5 curl
```

If you are using an OpenvCloud Ubuntu, please be sure the hostname is well set:
```
grep $(hostname) /etc/hosts || sed -i "s/.1 localhost/.1 localhost $(hostname)/g" /etc/hosts
```

Then you can run the following command:
```
cd /tmp; rm -f install.sh; curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh;bash install.sh
```

Mac OSX
-------
- Make sure Brew and curl are installed
- Go to the shell in Mac OSX:
```shell
export TMPDIR=~/tmp;mkdir -p $TMPDIR;cd $TMPDIR;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh;bash install.sh
```

Reset your system
-----------------
If your installation failed or if you want to remove your current installation, you can execute the following commands:
```shell
export TMPDIR=~/tmp;cd $TMPDIR;rm -f reset.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/reset.sh > reset.sh;bash reset.sh
```


Environment arguments which can be set to change behavior of installation
-------------------------------------------------------------------------

```
export GITHUBUSER=''
export GITHUBPASSWD=''
export JSBASE='/opt/jumpscale8'
export JSGIT='https://github.com/Jumpscale/jumpscale_core8.git'
export AYSGIT='https://github.com/Jumpscale/ays_jumpscale8.git'
```

* JSBASE: root directory where JumpScale will be installed
* GITHUBUSER: user used to connect to GitHub
* GITHUBPASSWD: password used to connect to GitHub
* JSGIT & AYSGIT: allow us to choose other installation sources for JumpScale as well as AtYourService repo

The default branch = master

Detailed installation process
=============================
If you want to know more about the installation process you can check a more detailed documentation:
- [Install Process Details](../BeyondBasics/Install%20Process%20Details.md)


Test JumpScale
--------------
The easiest way to get to know the framework well is to start an interactive shell, to test if that works, execute the following command:
```shell
js
```

You can also test using the JumpScale framework as a library in your code, to test if that works, execute the following command:
```shell
ipython
from JumpScale import j
```