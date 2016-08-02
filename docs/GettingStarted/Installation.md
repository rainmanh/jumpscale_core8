## Installation

### Supported platforms

- Ubuntu 14+
- Mac OSX Yosemite
- Windows 10 (Cygwin)


### Requirements

- Python 3.5
- curl


### Ubuntu

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

Then you can run the following command:
```shell
cd /tmp
rm -f install.sh
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh;bash install.sh
```

### Mac OSX

- Make sure Brew and curl are installed
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install curl
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


### Windows 10 (Cygwin)

 - Install [Cygwin](https://cygwin.com/install.html)
 - When installing Cygwin search for the following packages in the package menu and select them:
     - [curl](https://curl.haxx.se/), under net
     - [gcc-g+_+ :gnu compiler collection(c ++)](https://en.wikipedia.org/wiki/GNU_Compiler_Collection), under devel  
     - [mc](https://www.midnight-commander.org/), under shell
     - [Paramiko](http://www.paramiko.org/), under python
 - Install apt-cyg through:

```shell
lynx -source rawgit.com/transcode-open/apt-cyg/master/apt-cyg > apt-cyg
install apt-cyg /bin
```

Then to install JumpScale:

```shell
cd /tmp
rm -f install.sh
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh
bash install.sh
```

### Reset your system

If your installation failed or if you want to remove your current installation, you can execute the following commands:

```shell
export TMPDIR=~/tmp
cd $TMPDIR
rm -f reset.sh
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/reset.sh > reset.sh
bash reset.sh
```


###  Environment variables that influence the installation process

```
GITHUBUSER = ''
GITHUBPASSWD = ''
SANDBOX = 0
JSBASE = '/opt/jumpscale8'
JSGIT = 'https://github.com/Jumpscale/jumpscale_core8.git'
JSBRANCH = 'master'
AYSGIT = 'https://github.com/Jumpscale/ays_jumpscale8.git'
AYSBRANCH = 'master'
CODEDIR = '/opt/code'
```

- JSBASE: root directory where JumpScale will be installed
- GITHUBUSER: user used to connect to GitHub
- GITHUBPASSWD: password used to connect to GitHub
- JSGIT & AYSGIT: allow us to choose other installation sources for JumpScale as well as AtYourService repo


### More detailed about installation process

Several scripts are involved to complete the installation:

- [install.sh](https://github.com/Jumpscale/jumpscale_core8/blob/master/install/install.sh): this is the main entry point of the installation process, it will make sure that at least Python 3 and curl packages are installed, then it will download `bootstrap.py`, the second installation script, and run it it.
- [bootstrap.py](https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/web/bootstrap.py): this is a very simple script that only downloads the `InstallTools.py` script and execute the main installation function.
- [InstallTools.py](https://github.com/Jumpscale/jumpscale_core8/blob/master/install/InstallTools.py): this script includes all the helpers functions to install the whole JumpScale framework on your system. The main function of the installer is the following `installJS` function from the `InstallTools.py` script

```python
installJS(self,base="",clean=False,insystem=True,GITHUBUSER="",GITHUBPASSWD="",CODEDIR="",\
        JSGIT="https://github.com/Jumpscale/jumpscale_core8.git",JSBRANCH="master",\
        AYSGIT="https://github.com/Jumpscale/ays_jumpscale8",AYSBRANCH="master",SANDBOX=0,EMAIL="",FULLNAME=""):
        """

        @param insystem means use system packaging system to deploy dependencies like python & python packages
        @param codedir is the location where the code will be installed, code which get's checked out from github
        @param base is location of root of JumpScale
        @copybinary means copy the binary files (in sandboxed mode) to the location, don't link

        JSGIT & AYSGIT allow us to chose other install sources for jumpscale as well as AtYourService repo

        IMPORTANT: if env var's are set they get priority

        """
```
