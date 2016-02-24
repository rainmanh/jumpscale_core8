
from JumpScale import j





from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.installerdevelop"


class CuisineInstallerDevelop():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    @actionrun(action=True)
    def python(self):
        C="""
        libpython3.5-dev
        python3.5-dev
        libffi-dev
        gcc
        make
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
        C="""
            #important remove olf pkg_resources, will conflict with new pip
            rm -rf /usr/lib/python3/dist-packages/pkg_resources
            cd $tmpDir/
            rm -rf get-pip.py
            wget https://bootstrap.pypa.io/get-pip.py
            """
        C=self.cuisine.args_replace(C)
        self.cuisine.run_script(C)
        C="cd $tmpDir/;python3.5 get-pip.py"
        C=self.cuisine.args_replace(C)
        self.cuisine.run(C)


    @actionrun(action=True)
    def jumpscale8(self):
        #make sure base is done & env is clean
        self.cuisine.installer.base()

        self.python()
        self.pip(action=True)

        #install brotli
        C="""
        cd $tmpDir/
        sudo rm -rf brotli/
        git clone https://github.com/google/brotli.git
        cd $tmpDir/brotli/
        python setup.py install
        cd tests
        make
        cd ..
        cp $tmpDir/brotli/tools/bro /usr/local/bin/
        rm -rf $tmpDir/brotli
        """
        C=self.cuisine.args_replace(C)
        self.cuisine.run_script(C,action=True)

        #python etcd
        C="""
        cd $tmpDir/
        git clone https://github.com/jplana/python-etcd.git
        cd python-etcd
        python3.5 setup.py install
        """
        C=self.cuisine.args_replace(C)
        self.cuisine.run_script(C,action=True)


        C="""
        paramiko

        msgpack-python
        redis
        #credis
        aioredis


        mongoengine

        #bcrypt
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
        python-etcd
        websocket
        marisa-trie
        pylzma
        ujson
        watchdog
        pygo
        minio
        
        python-telegram-bot
        """
        self.cuisine.pip.multiInstall(C,action=True,upgrade=True)

        #gevent
        C="""
        pip3 install 'cython>=0.23.4' git+git://github.com/gevent/gevent.git#egg=gevent
        """
        self.cuisine.run_script(C,action=True)

        self.cuisine.builder.redis()

        if self.cuisine.isUbuntu or self.cuisine.isArch:
            C='cd $tmpDir/;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh;bash install.sh'
            C=self.cuisine.args_replace(C)
            self.cuisine.run(C,action=True)
        elif self.cuisine.isMac:
            cmd = """sudo mkdir -p /opt
            # sudo chown -R despiegk:root /opt
            ruby -e \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)\""""
            self.cuisine.run(cmd)
        else:
            raise RuntimeError("platform not supported yet")
