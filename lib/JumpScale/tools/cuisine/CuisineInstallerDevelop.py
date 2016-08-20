from JumpScale import j


from ActionDecorator import ActionDecorator


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.installerdevelop"

base = j.tools.cuisine.getBaseClass()


class CuisineInstallerDevelop(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def python(self):
        if self._cuisine.platformtype.osname == "debian":
            C = """
            libpython3.4-dev
            python3.4-dev
            """
        elif self._cuisine.platformtype.osname == 'ubuntu' and self._cuisine.platformtype.osversion == '16.04':
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
        self._cuisine.package.multiInstall(C)

        C = """
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
        vim
        #net-tools
        """
        self._cuisine.package.multiInstall(C)

    def pip(self):
        self._cuisine.installer.base()
        self.python()
        if self._cuisine.core.isMac:
            return

        C = """
            #important remove olf pkg_resources, will conflict with new pip
            rm -rf /usr/lib/python3/dist-packages/pkg_resources
            cd $tmpDir/
            rm -rf get-pip.py
            wget --remote-encoding=utf-8 https://bootstrap.pypa.io/get-pip.py
            """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.run_script(C)
        C = "cd $tmpDir/;python3 get-pip.py"
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.run(C)

    def installJS8Deps(self):
        # make sure base is done & env is clean
        # self._cuisine.installer.base()

        self.python()
        self.pip(action=True)
        self.brotli()

        self._cuisine.pip.install('pytoml')
        self._cuisine.pip.install('pygo')

        # python etcd
        C = """
        cd $tmpDir/
        git clone https://github.com/jplana/python-etcd.git
        cd python-etcd
        python3 setup.py install
        """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.run_script(C)

        # gevent
        C = """
        pip3 install 'cython>=0.23.4' git+git://github.com/gevent/gevent.git#egg=gevent
        """
        self._cuisine.core.run_script(C)

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
        """
        self._cuisine.pip.multiInstall(C, upgrade=True)

        if self._cuisine.platformtype.osname != "debian":
            C = """
            blosc
            bcrypt
            """
            self._cuisine.pip.multiInstall(C, upgrade=True)

        if not self._cuisine.core.isCygwin:
            self._cuisine.apps.redis.build()

    def jumpscale8(self):
        if self._cuisine.installer.jumpscale_installed():
            return
        self.installJS8Deps(force=False)

        if self._cuisine.core.isUbuntu or self._cuisine.core.isArch:

            if self._cuisine.core.dir_exists("/usr/local/lib/python3.4/dist-packages"):
                linkcmd = "mkdir -p /usr/local/lib/python3.5/dist-packages/JumpScale;ln -s /usr/local/lib/python3.5/dist-packages/JumpScale /usr/local/lib/python3.4/dist-packages/JumpScale"
                self._cuisine.core.run(linkcmd)

            C = 'cd $tmpDir/;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh;bash install.sh'
            C = self._cuisine.core.args_replace(C)
            self._cuisine.core.run(C)
        elif self._cuisine.core.isMac:
            cmd = "export TMPDIR=~/tmp;mkdir -p $TMPDIR;cd $TMPDIR;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh;bash install.sh"
            self._cuisine.core.run(cmd)
        else:
            raise j.exceptions.RuntimeError("platform not supported yet")

    def cleanup(self, aggressive=False):
        self._cuisine.core.run("apt-get clean")
        self._cuisine.core.dir_remove("/var/tmp/*")
        self._cuisine.core.dir_remove("/etc/dpkg/dpkg.cfg.d/02apt-speedup")
        self._cuisine.core.dir_remove("$tmpDir")
        self._cuisine.core.dir_ensure("$tmpDir")

        self._cuisine.core.dir_remove("$goDir/src/*")
        self._cuisine.core.dir_remove("$tmpDir/*")
        self._cuisine.core.dir_remove("$varDir/data/*")
        self._cuisine.core.dir_remove('/opt/code/github/domsj', True)
        self._cuisine.core.dir_remove('/opt/code/github/openvstorage', True)

        C = """
        cd /opt;find . -name '*.pyc' -delete
        cd /opt;find . -name '*.log' -delete
        cd /opt;find . -name '__pycache__' -delete
        """
        self._cuisine.core.run_script(C)

        if aggressive:
            C = """
            set -ex
            cd /
            find -regex '.*__pycache__.*' -delete
            rm -rf /var/log
            mkdir -p /var/log/apt
            rm -rf /var/tmp
            mkdir -p /var/tmp
            rm -rf /usr/share/doc
            mkdir -p /usr/share/doc
            rm -rf /usr/share/gcc-5
            rm -rf /usr/share/gdb
            rm -rf /usr/share/gitweb
            rm -rf /usr/share/info
            rm -rf /usr/share/lintian
            rm -rf /usr/share/perl
            rm -rf /usr/share/perl5
            rm -rf /usr/share/pyshared
            rm -rf /usr/share/python*
            rm -rf /usr/share/zsh

            rm -rf /usr/share/locale-langpack/en_AU
            rm -rf /usr/share/locale-langpack/en_CA
            rm -rf /usr/share/locale-langpack/en_GB
            rm -rf /usr/share/man

            rm -rf /usr/lib/python*
            rm -rf /usr/lib/valgrind

            rm -rf /usr/bin/python*
            """
            self._cuisine.core.run_script(C)

    def brotli(self):
        C = """
        cd /tmp
        sudo rm -rf brotli/
        git clone https://github.com/google/brotli.git
        cd /tmp/brotli/
        ./configure
        make bro
        cp /tmp/brotli/bin/bro /usr/local/bin/
        rm -rf /tmp/brotli
        """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.run_script(C)

    def xrdp(self):
        """
        builds a full xrdp, this can take a while
        """
        C = """
        cd /root
        git clone https://github.com/scarygliders/X11RDP-o-Matic.git
        cd X11RDP-o-Matic
        bash X11rdp-o-matic.sh
        ln -fs /usr/bin/Xvfb /etc/X11/X
        apt-get update
        apt-get install  -y --force-yes lxde lxtask
        echo 'pgrep -U $(id -u) lxsession | grep -v ^$_LXSESSION_PID | xargs --no-run-if-empty kill' > /bin/lxcleanup.sh
        chmod +x /bin/lxcleanup.sh
        echo '@lxcleanup.sh' >> /etc/xdg/lxsession/LXDE/autostart
        echo '#!/bin/sh -xe\nrm -rf /tmp/* /var/run/xrdp/* && service xrdp start && startx' > /bin/rdp.sh
        chmod +x /bin/rdp.sh
        """
        self._cuisine.core.run_script(C)
