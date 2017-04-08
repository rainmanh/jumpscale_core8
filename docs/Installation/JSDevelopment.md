# Installation

## Supported platforms

- Ubuntu 14+
- Mac OSX Yosemite
- Windows 10 (Cygwin): EARLY DRAFT

## Requirements

- Minimum 2GB RAM
- Python 3.5
- curl

## Ubuntu

Use the below installation script to make your life easy.

> Note: If you can install it as root, do it, otherwise please use `sudo -s -H`

```shell
sudo -s -H
apt-get update
apt-get -y dist-upgrade
apt-get install -y python3.5 curl
```

If you are using an image of Ubuntu prepared for [OpenvCloud](https://gig.gitbooks.io/ovcdoc_public/content/), please be sure the hostname is well set:

```
grep $(hostname) /etc/hosts || sed -i "s/.1 localhost/.1 localhost $(hostname)/g" /etc/hosts
```

Then you can run the following command, in this case for installing the 8.1.1 branch:

```shell
cd /tmp
rm -f install.sh
export JSBRANCH="8.1.1"
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/${JSBRANCH}/install/install.sh > install.sh
bash install.sh
```

## Mac OSX

- Make sure Brew and curl are installed:

```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install curl
brew install python3
```

- install pip3:

```
sudo -s
cd ~/tmp;curl -k https://bootstrap.pypa.io/get-pip.py > get-pip.py;python3 get-pip.py
```

- Go to the shell in Mac OSX:

```shell
export TMPDIR=~/tmp
mkdir -p $TMPDIR
cd $TMPDIR
rm -f install.sh
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh
bash install.sh
```


## Reset your system

If your installation failed or if you want to remove your current installation, you can execute the following commands:

```shell
export TMPDIR=~/tmp
cd $TMPDIR
rm -f reset.sh
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/reset.sh > reset.sh
bash reset.sh
```


##  Environment variables that influence the installation process

None of the following environment variables are required, but can all optionally be set:

```
DEBUG = 0
GITHUBUSER = ''
SANDBOX = 0
JSBASE = #'/opt/jumpscale8' on ubuntu if /JS8 does not exist, else $HOME/opt/jumpscale8
JSBRANCH = 'master'
AYSBRANCH = 'master'
CODEDIR = #'/opt/code' on ubuntu if /JS8 does not exist, else $HOME/opt/code
TMPDIR = #default is $HOME/tmp if not set
HOME = #homedir of your system
CFGDIR = #'/opt/jumpscale8/cfg' on ubuntu if /JS8 does not exist, else $HOME/optvar/cfg
DATADIR = #'/optvar/data' on ubuntu if /JS8 does not exist, else $HOME/optvar/data

```

- **JSBASE**: root directory where JumpScale will be installed
- **GITHUBUSER**: user used to connect to GitHub (only relevant when connecting to GitHub over HTTP)

  > It is strongly recommended to use SSH to access GitHub instead of HTTP, using ```ssh-add``` to load your private ssh-key(s)

Setting these environment variables on Linux and OSX is simple:

```
export JSBRANCH="fix_installer"
```

## Windows 10 (Cygwin)

 - Install [Cygwin](https://cygwin.com/install.html)
 - When installing Cygwin search for the following packages in the package menu and select them:
     - [curl](https://curl.haxx.se/), under net
     - [gcc-g++ :gnu compiler collection(c ++)](https://en.wikipedia.org/wiki/GNU_Compiler_Collection), under devel
     - [Paramiko](http://www.paramiko.org/), under python
     - [lynx](http://lynx.browser.org/lynx.html), under web

Then to install JumpScale:

```shell
cd /tmp
rm -f install.sh
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh
bash install.sh
```

```
!!!
title = "JSDevelopment"
date = "2017-04-08"
tags = []
```
