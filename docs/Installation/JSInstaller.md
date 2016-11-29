# More Details about the Installation Process

Several scripts are involved to complete the installation:

- [install.sh](https://github.com/Jumpscale/jumpscale_core8/blob/master/install/install.sh) is the main entry point of the installation process, it will make sure that at least Python 3 and curl packages are installed, then it will download `bootstrap.py`, the second installation script, and run it it
- [bootstrap.py](https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/bootstrap.py) is a very simple script that only downloads the `InstallTools.py` script and executes the main installation function
- [InstallTools.py](https://github.com/Jumpscale/jumpscale_core8/blob/master/install/InstallTools.py) includes all the helpers functions to install the whole JumpScale framework on your system. The main function of the installer is the following `installJS` function from the `InstallTools.py` script

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




## Dependencies (needs to be verified)

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
