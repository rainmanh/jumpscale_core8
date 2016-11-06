
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
        """
        self.do.execute("apt-get install libssl-dev")
        self.do.pip(C, executor=executor)

    def portal(self, executor=None):
        C = """
        mongoengine
        """
        self.do.pip(C, executor=executor)

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
