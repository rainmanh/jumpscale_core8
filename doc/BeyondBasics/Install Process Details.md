# Installation process details

## Supported platforms

- Ubuntu 14+
- Mac OSX Yosemite

## Following environment variables influence the installation process

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

## JumpScale installation process

Several scripts are involved to complete the installation:
- [install.sh](https://github.com/Jumpscale/jumpscale_core8/blob/master/install/install.sh): this is the main entry point of the installation process, it will make sure that at least python3 and curl packages are installed, then it will download `bootstrap.py`, the second installation script, and run it it.
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