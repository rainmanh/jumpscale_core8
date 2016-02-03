
from JumpScale import j

from CuisinePortal import CuisinePortal



from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.installerdevelop"


class CuisineInstallerDevelop():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine
        self._portal = None

    @property
    def portal(self):
        if self._portal is None:
            self._portal = CuisinePortal(self.executor, self.cuisine)
        return self._portal

    def python(self):
        C="""
        libpython3.5-dev
        python3.5-dev
        libffi-dev
        gcc
        build-essential
        autoconf
        libtool
        pkg-config
        libpq-dev
        libsqlite3-dev
        #net-tools
        """
        self.cuisine.package.multiInstall(C)

    @actionrun(action=True)
    def pip(self):
        self.cuisine.installer.base()
        self.python()
        cmd="""
            cd /tmp
            rm -rf get-pip.py
            wget https://bootstrap.pypa.io/get-pip.py
        """
        self.cuisine.run_script(cmd)
        self.cuisine.run("cd /tmp;python3.5 get-pip.py")


    @actionrun(action=True)
    def jumpscale(self):

        self.pip(action=True)

        C = """
        set +ex
        pskill redis-server #will now kill too many redis'es, should only kill the one not in docker
        pskill redis #will now kill too many redis'es, should only kill the one not in docker
        umount -fl /optrw
        # apt-get remove redis-server -y
        rm -rf /overlay/js_upper
        rm -rf /overlay/js_work
        rm -rf /optrw
        js8 stop
        pskill js8
        umount -f /opt
        apt-get install tmux fuse -y
        """
        self.cuisine.run_script(C,action=True)

        #install brotli
        C="""
        cd /tmp
        sudo rm -rf brotli/
        git clone https://github.com/google/brotli.git
        cd /tmp/brotli/
        python setup.py install
        cd tests
        make
        cd ..
        cp /tmp/brotli/tools/bro /usr/local/bin/
        rm -rf /tmp/brotli
        """
        self.cuisine.run_script(C,action=True)

        #python etcd
        C="""
        cd /tmp
        git clone https://github.com/jplana/python-etcd.git
        cd python-etcd
        python3.5 setup.py install
        """
        self.cuisine.run_script(C,action=True)


        C="""
        paramiko

        msgpack-python
        redis
        credis
        aioredis


        mongoengine

        bcrypt
        blosc
        certifi
        docker-py

        gitlab3
        gitpython
        html2text

        # pysqlite
        click
        influxdb
        ipdb
        ipython --upgrade
        jinja2
        netaddr

        reparted
        pytoml
        pystache
        pymongo
        psycopg2
        pathtools
        psutil

        pytz
        requests
        sqlalchemy
        urllib3
        zmq
        pyyaml
        websocket
        marisa-trie
        pylzma
        ujson
        watchdog
        """
        self.cuisine.pip.multiInstall(C,action=True,upgrade=True)

        #gevent
        C="""
        pip3 install 'cython>=0.23.4' git+git://github.com/gevent/gevent.git#egg=gevent
        """
        self.cuisine.run_script(C,action=True)

    @actionrun(action=True)
    def jumpscale8(self):

        self.cuisine.installer.pip()
        self.cuisine.pip.upgrade("pip")
        libDeps = ["'cython>=0.23.4' git+git://github.com/gevent/gevent.git#egg=gevent", "paramiko", "msgpack-python", "redis", "credis", "aioredis", "mongoengine", "bcrypt",
         "blosc", "certifi", "docker-py", "gitlab3", "gitpython", "html2text","click", "influxdb", "ipdb", "ipython", "jinja2",
         "netaddr", "reparted", "pytoml", "pystache", "pymongo", "psycopg2", "pathtools", "psutil", "pytz", "requests", "sqlalchemy",
          "urllib3", "zmq", "pyyaml", "websocket", "marisa-trie", "pylzma", "ujson", "watchdog"]
        for dep in libDeps:
            self.cuisine.pip.install(dep)

        if self.cuisine.isUbuntu:
            self.cuisine.run('cd /tmp;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh;bash install.sh')
        elif self.cuisine.isMac:
            cmd = """sudo mkdir -p /opt
            sudo chown -R despiegk:root /opt
            ruby -e \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)\""""
            self.cuisine.run(cmd)
        else:
            raise RuntimeError("platform not supported yet")
    #@todo installer for trueid env
    #@todo installer for g8exchange
