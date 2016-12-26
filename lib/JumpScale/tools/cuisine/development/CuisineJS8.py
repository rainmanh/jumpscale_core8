from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisineJS8(base):

    def jumpscale_installed(self, die=False):
        rc1, out1, err = self.cuisine.core.run('which js8', die=False)
        rc2, out2, err = self.cuisine.core.run('which js', die=False)
        if (rc1 == 0 and out1) or (rc2 == 0 and out2):
            return True
        return False

    def install(self, reset=False, deps=True, branch='master', keep=False):

        if reset is False and self.jumpscale_installed():
            return

        if deps:
            self.installDeps()

        if self.cuisine.core.isUbuntu or self.cuisine.core.isArch:

            if self.cuisine.core.dir_exists("/usr/local/lib/python3.4/dist-packages"):
                linkcmd = "mkdir -p /usr/local/lib/python3.5/dist-packages/JumpScale;ln -s /usr/local/lib/python3.5/dist-packages/JumpScale /usr/local/lib/python3.4/dist-packages/JumpScale"
                self.cuisine.core.run(linkcmd)

            C = 'cd $TMPDIR/;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/{branch}/install/install.sh > install.sh;JSBRANCH={branch} bash install.sh'.format(
                branch=branch)
            if keep:
                C += ' -k'

            C = self.replace(C)
            self.cuisine.core.run(C)
        elif self.cuisine.core.isMac:
            cmd = "export TMPDIR=~/tmp;mkdir -p $TMPDIR;cd $TMPDIR;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/{branch}/install/install.sh > install.sh;JSBRANCH={branch} bash install.sh".format(
                branch=branch)
            if cmd:
                cmd += ' -k'
            self.cuisine.core.run(cmd)
        else:
            raise j.exceptions.RuntimeError("platform not supported yet")

    def installDeps(self):

        self.cuisine.systemservices.base.install()
        self.cuisine.development.python.install()
        self.cuisine.development.pip.ensure()
        self.cuisine.apps.redis.install()
        self.cuisine.apps.brotli.build()
        self.cuisine.apps.brotli.install()

        self.cuisine.development.pip.install('pytoml')
        self.cuisine.development.pip.install('pygo')
        self.cuisine.package.ensure('libxml2-dev')
        self.cuisine.package.ensure('libxslt1-dev')

        # python etcd
        C = """
        cd $TMPDIR/
        git clone https://github.com/jplana/python-etcd.git
        cd python-etcd
        python3 setup.py install
        """
        C = self.replace(C)
        self.cuisine.core.execute_bash(C)

        # gevent
        C = """
        pip3 install 'cython>=0.23.4' git+git://github.com/gevent/gevent.git#egg=gevent
        """
        self.cuisine.core.execute_bash(C)

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
        pycapnp
        """
        self.cuisine.development.pip.multiInstall(C, upgrade=True)

        # snappy install
        self.cuisine.package.ensure('libsnappy-dev')
        self.cuisine.package.ensure('libsnappy1v5')
        self.cuisine.development.pip.install('python-snappy')

        if self.cuisine.platformtype.osname != "debian":
            C = """
            blosc
            bcrypt
            """
            self.cuisine.development.pip.multiInstall(C, upgrade=True)
