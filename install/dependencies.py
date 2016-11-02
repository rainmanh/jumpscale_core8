
class dependencies():

    def all(self, executor=None):
        C = """
        redis
        paramiko
        watchdog
        gitpython
        click
        pymux
        uvloop
        yaml
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
        do.installer.pip(C, executor=executor)

    def portal(self, executor=None):
        C = """
        mongoengine
        uvloop
        """
        do.installer.pip(C, executor=executor)

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
