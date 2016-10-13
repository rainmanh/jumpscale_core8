from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisineJS8(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def jumpscale_installed(self, die=False):
        rc1, out1, err = self._cuisine.core.run('which js8', die=False)
        rc2, out2, err = self._cuisine.core.run('which js', die=False)
        if (rc1 == 0 and out1) or (rc2 == 0 and out2):
            return True
        return False

    def install(self, reset=False, deps=True, branch='master'):

        if reset is False and self.jumpscale_installed():
            return

        if deps:
            self.installDeps()

        if self._cuisine.core.isUbuntu or self._cuisine.core.isArch:

            if self._cuisine.core.dir_exists("/usr/local/lib/python3.4/dist-packages"):
                linkcmd = "mkdir -p /usr/local/lib/python3.5/dist-packages/JumpScale;ln -s /usr/local/lib/python3.5/dist-packages/JumpScale /usr/local/lib/python3.4/dist-packages/JumpScale"
                self._cuisine.core.run(linkcmd)

            C = 'cd $tmpDir/;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/{branch}/install/install.sh > install.sh;bash install.sh'.format(branch=branch)
            C = self._cuisine.core.args_replace(C)
            self._cuisine.core.run(C)
        elif self._cuisine.core.isMac:
            cmd = "export TMPDIR=~/tmp;mkdir -p $TMPDIR;cd $TMPDIR;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/{branch}/install/install.sh > install.sh;bash install.sh".format(branch=branch)
            self._cuisine.core.run(cmd)
        else:
            raise j.exceptions.RuntimeError("platform not supported yet")

    def installDeps(self):

        self._cuisine.systemservices.base.install()
        self._cuisine.development.python.install()
        self._cuisine.development.pip.ensure()
        self._cuisine.apps.redis.install()
        self._cuisine.apps.brotli.build()

        self._cuisine.development.pip.install('pytoml')
        self._cuisine.development.pip.install('pygo')

        # python etcd
        C = """
        cd $tmpDir/
        git clone https://github.com/jplana/python-etcd.git
        cd python-etcd
        python3 setup.py install
        """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.execute_bash(C)

        # gevent
        C = """
        pip3 install 'cython>=0.23.4' git+git://github.com/gevent/gevent.git#egg=gevent
        """
        self._cuisine.core.execute_bash(C)

        C = """
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
        http://carey.geek.nz/code/python-fcrypt/fcrypt-1.3.1.tar.gz

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
        gspread
        oauth2client
        crontab
        beautifulsoup4
        lxml

        snappy
        """
        self._cuisine.development.pip.multiInstall(C, upgrade=True)

        if self._cuisine.platformtype.osname != "debian":
            C = """
            blosc
            bcrypt
            """
            self._cuisine.development.pip.multiInstall(C, upgrade=True)
