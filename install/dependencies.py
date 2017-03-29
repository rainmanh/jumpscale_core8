
class dependencies():

    def __init__(self, do):
        self.do = do

    def all(self, executor=None):
        C = """
        uvloop
        redis
        paramiko
        watchdog
        gitpython
        click
        pymux
        uvloop
        pyyaml
        ipdb
        requests
        netaddr
        ipython
        cython
        pycapnp
        path.py
        colored-traceback
        pudb
        colorlog
        msgpack-python
        pyblake2
        brotli
        pysodium
        ipfsapi
        curio
        asyncssh
        autopep8
        pytoml
        sanic
        jsonschema
        peewee
        docker
        toml
        pystache
        colorlog
        """
        self.do.pip(C, executor=executor)
        self.do.execute("pip3 install https://github.com/tony/libtmux/archive/master.zip --upgrade")

    def portal(self, executor=None):
        C = """
        mongoengine
        """
        self.do.pip(C, executor=executor)

    def flist(self, executor=None):
        self.do.execute("apt-get install -y librocksdb-dev libhiredis-dev libbz2-dev", executor=executor)
        self.do.pip("pyrocksdb peewee g8storclient", executor=executor)

    # OBSOLETE
    # """
    # all
    # hiredis
    # ptpython
    # ptpdb
    #  pip3 install --upgrade http://carey.geek.nz/code/python-fcrypt/fcrypt-1.3.1.tar.gz
    #  dulwich
    #  git
    #  xonsh
    # """
