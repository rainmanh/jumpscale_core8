from JumpScale import j





from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.installerdevelop"


class CuisineInstallerDevelop:

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    @actionrun(action=True)
    def python(self):
        if self.cuisine.platformtype.osname == "debian":
            C = """
            libpython3.4-dev
            python3.4-dev
            """
        elif self.cuisine.platformtype.osname == 'ubuntu' and self.cuisine.platformtype.osversion == '16.04':
            C = """
            libpython3.5-dev
            python3.5-dev
            """
        else:
            C = """
            python3
            postgresql
            libpython3.4-dev
            python3.4-dev
            libpython3.5-dev
            python3.5-dev
            """
        self.cuisine.package.multiInstall(C)

        C="""
        autoconf
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
        if self.cuisine.core.isMac:
            return
        
        C="""
            #important remove olf pkg_resources, will conflict with new pip
            rm -rf /usr/lib/python3/dist-packages/pkg_resources
            cd $tmpDir/
            rm -rf get-pip.py
            wget --remote-encoding=utf-8 https://bootstrap.pypa.io/get-pip.py
            """
        C=self.cuisine.core.args_replace(C)
        self.cuisine.core.run_script(C)
        C="cd $tmpDir/;python3 get-pip.py"
        C=self.cuisine.core.args_replace(C)
        self.cuisine.core.run(C)

    @actionrun(action=True)
    def installJS8Deps(self):
        #make sure base is done & env is clean
        self.cuisine.installer.base()

        self.python()
        self.pip(action=True)

        if not self.cuisine.core.isArch:
            #install brotli
            C="""
            cd $tmpDir/
            sudo rm -rf brotli/
            git clone https://github.com/google/brotli.git
            cd $tmpDir/brotli/
            python setup.py install
            cd tools
            make
            cp $tmpDir/brotli/tools/bro /usr/local/bin/
            rm -rf $tmpDir/brotli
            """
            C=self.cuisine.core.args_replace(C)
            self.cuisine.core.run_script(C,force=False)

        #python etcd
        C="""
        cd $tmpDir/
        git clone https://github.com/jplana/python-etcd.git
        cd python-etcd
        python3 setup.py install
        """
        C=self.cuisine.core.args_replace(C)
        self.cuisine.core.run_script(C,force=False)

        #gevent
        C="""
        pip3 install 'cython>=0.23.4' git+git://github.com/gevent/gevent.git#egg=gevent
        """
        self.cuisine.core.run_script(C,force=False)

        C="""
        # cffi==1.5.2
        cffi
        paramiko

        msgpack-python
        redis
        #credis
        aioredis

        mongoengine==0.10.6

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
        wtforms_json

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
        pygithub
        minio

        # colorlog
        colored-traceback
        #pygments
        tmuxp

        ply
        xonsh
        pudb

        traitlets
        python-telegram-bot
        colorlog
        path.py
        dnspython3
        packet-python
        """
        self.cuisine.pip.multiInstall(C,upgrade=True)


        if self.cuisine.platformtype.osname!="debian":
            C="""
            blosc
            bcrypt
            """
            self.cuisine.pip.multiInstall(C,upgrade=True)

        self.cuisine.apps.redis.build()


    @actionrun(action=True)
    def jumpscale8(self):
        if self.cuisine.installer.jumpscale_installed():
            return
        self.installJS8Deps(force=False)

        if self.cuisine.core.isUbuntu or self.cuisine.core.isArch:

            if self.cuisine.core.dir_exists("/usr/local/lib/python3.4/dist-packages"):
                linkcmd="mkdir -p /usr/local/lib/python3.5/dist-packages/JumpScale;ln -s /usr/local/lib/python3.5/dist-packages/JumpScale /usr/local/lib/python3.4/dist-packages/JumpScale"
                self.cuisine.core.run(linkcmd)

            C='cd $tmpDir/;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh;bash install.sh'
            C=self.cuisine.core.args_replace(C)
            self.cuisine.core.run(C)
        elif self.cuisine.core.isMac:
            cmd = "export TMPDIR=~/tmp;mkdir -p $TMPDIR;cd $TMPDIR;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh;bash install.sh"
            self.cuisine.core.run(cmd)
        else:
            raise j.exceptions.RuntimeError("platform not supported yet")

    @actionrun(action=True)
    def cleanup(self):
        C="""
        #!/bin/bash
        set +ex
        apt-get clean
        rm -rf /var/tmp/*
        # rm -rf /var/lib/apt/lists/*
        rm -f /etc/dpkg/dpkg.cfg.d/02apt-speedup
        #rm -f /etc/ssh/ssh_host_*
        """
        C=self.cuisine.core.args_replace(C)
        self.cuisine.core.run_script(C,force=True)

    @actionrun(action=True)
    def brotli(self):
        C="""
        cd /tmp
        sudo rm -rf brotli/
        git clone https://github.com/google/brotli.git
        cd /tmp/brotli/
        ./configure
        make
        cp /tmp/brotli/bin/bro /usr/local/bin/
        rm -rf /tmp/brotli
        """
        C=self.cuisine.core.args_replace(C)
        self.cuisine.core.run_script(C,force=True)