# Installation

## Supported platforms

- Ubuntu 14+
- Mac OSX Yosemite
- Windows 10 (Cygwin)


## Requirements

- Minimuam 2GB RAM
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

Then you can run the following command:
```shell
cd /tmp
rm -f install.sh
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh
bash install.sh
```

## Mac OSX

- Make sure Brew and curl are installed
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install curl
brew install python3
```

- install pip3
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


## Dependencies
To minimize the size of the installation some of the dependencies were opted to be installed separately, only
dependencies which affect modular components of JumpScale where moved out to allow JumpScale's key components to function
normally without the dependencies. For example:
 - a module such as [**cuisine**](../../Cuisine/Cuisine.md) dependeds on  [**paramiko**](http://docs.paramiko.org/en/2.0/)

To install the dependencies run this command in the shell:
```shell
js 'j.tools.cuisine.local.development.js8.installDeps()'
```

Here is a list of the dependencies:
 - [**redis**](http://redis.io/)
 - [**brotli**](https://github.com/google/brotli)
 - [**pip**](https://pypi.python.org/pypi/pip)
 - [**etcd**](https://github.com/coreos/etcd)
 - [**cython**](http://cython.org/)
 - python package [**pytoml**](https://github.com/avakar/pytoml)
 - python package [**pygo**](https://github.com/muhamadazmy/python-pygo)
 - python package [**cffi**](https://cffi.readthedocs.io/en/latest/)
 - python package [**paramiko**](http://docs.paramiko.org/en/2.0/)
 - python package [**msgpack**-python](https://pypi.python.org/pypi/msgpack-python)
 - python package [**redis**](https://redis-py.readthedocs.io/en/latest/)
 - python package [**aioredis**](https://github.com/aio-libs/aioredis)
 - python package [**mongoengine**](http://mongoengine.org/)
 - python package [**certifi**](https://github.com/certifi/python-certifi)
 - python package [**docker-py**](https://github.com/docker/docker-py)
 - python package [**fcrypt**](http://words.carey.geek.nz/2004/02/python-fcrypt.html)
 - python package [**gitlab3**](https://github.com/alexvh/python-gitlab3)
 - python package [**gitpython**](http://gitpython.readthedocs.io/en/stable/)
 - python package [**html2text**](https://github.com/Alir3z4/html2text/)
 - python package [**click**](http://click.pocoo.org/5/)
 - python package [**influxdb**](https://github.com/influxdata/influxdb-python)
 - python package [**ipdb**](https://github.com/gotcha/ipdb)
 - python package [**ipython**](https://ipython.org/)
 - python package [**jinja2**](http://jinja.pocoo.org/docs/dev/)
 - python package [**netaddr**](https://pythonhosted.org/netaddr/)
 - python package [**wtforms_json**](https://wtforms-json.readthedocs.io/en/latest/)
 - python package [**reparted**](https://github.com/xzased/reparted)
 - python package [**pystache**](https://github.com/defunkt/pystache)
 - python package [**pymongo**](https://api.mongodb.com/python/current/)
 - python package [**psycopg2**](http://initd.org/psycopg/)
 - python package [**pathtools**](https://github.com/gorakhargosh/pathtools)
 - python package [**psutil**](https://github.com/giampaolo/psutil)
 - python package [**pytz**](https://github.com/newvem/pytz)
 - python package [**requests**](http://docs.python-requests.org/en/master/)
 - python package [**sqlalchemy**](http://www.sqlalchemy.org/)
 - python package [**urllib3**](https://urllib3.readthedocs.io/en/latest/)
 - python package [**zmq**](https://github.com/zeromq/libzmq)
 - python package [**pyyaml**](http://pyyaml.org/)
 - python package [**python-etcd**](https://github.com/jplana/python-etcd)
 - python package [**websocket**](https://github.com/aaugustin/websockets)
 - python package [**marisa-trie**](https://pypi.python.org/pypi/marisa-trie)
 - python package [**pylzma**](https://www.joachim-bauch.de/)
 - python package [**ujson**](https://github.com/esnme/ultrajson)
 - python package [**watchdog**](https://pypi.python.org/pypi/watchdog)
 - python package [**pygithub**](https://github.com/PyGithub/PyGithub)
 - python package [**minio**](https://github.com/minio/minio-py)
 - python package [**colored-traceback**](https://pypi.python.org/pypi/colored-traceback/0.2.0)
 - python package [**tmuxp**](https://github.com/tony/tmuxp)
 - python package [**ply**](https://github.com/dabeaz/ply)
 - python package [**xonsh**](https://github.com/xonsh/xonsh)
 - python package [**pudb**](https://pypi.python.org/pypi/pudb)
 - python package [**traitlets**](https://github.com/ipython/traitlets)
 - python package [**python-telegram-bot**](https://github.com/python-telegram-bot/python-telegram-bot)
 - python package [**colorlog**](https://github.com/borntyping/python-colorlog)
 - python package [**path.py**](https://github.com/jaraco/path.py)
 - python package [**dnspython3**](https://pypi.python.org/pypi/dnspython3)
 - python package [**packet-python**](https://pypi.python.org/pypi/packet/)
 - python package [**gspread**](https://github.com/burnash/gspread)
 - python package [**oauth2client**](https://github.com/google/oauth2client)
 - python package [**crontab**](https://pypi.python.org/pypi/python-crontab)
 - python package [**beautifulsoup4**](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
 - python package [**lxml**](http://lxml.de/)

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


## More details about installation process

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
