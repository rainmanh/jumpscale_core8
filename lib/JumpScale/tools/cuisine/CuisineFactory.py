from JumpScale import j

import inspect


class CuisineBase:

    def __init__(self, executor, cuisine):
        self._p_cache = None
        self.__classname = None
        self._executor = executor
        self._cuisine = cuisine
        # maybe best to still show the cuisine, is easier
        self.cuisine = cuisine

    @property
    def _classname(self):
        if self.__classname is None:
            self.__classname = str(self.__class__).split(".")[-1].strip("'>")
        return self.__classname

    def _reset(self):
        j.data.cache.reset(self._id)

    @property
    def _id(self):
        return self._executor.id

    @property
    def _cache(self):
        if self._p_cache is None:
            self._p_cache = j.data.cache.get(self._id, self._classname, keepInMem=False, reset=False)
        return self._p_cache

    def __str__(self):
        return "cuisine:%s:%s" % (getattr(self._executor, 'addr', 'local'), getattr(self._executor, 'port', ''))

    __repr__ = __str__


class CuisineApp(CuisineBase):

    NAME = None
    VERSION = None

    def isInstalled(self):
        """
        Checks if a package is installed or not
        You can ovveride it to use another way for checking
        """
        return self._cuisine.core.command_check(self.NAME)

    def install(self):
        if not self.isInstalled():
            raise NotImplementedError()


class CuisineBaseLoader:

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine
        myClassName = str(self.__class__).split(".")[-1].split("'")[0]
        localdir = j.sal.fs.getDirName(inspect.getsourcefile(self.__class__))
        classes = [j.sal.fs.getBaseName(item)[7:-3] for item in j.sal.fs.listFilesInDir(localdir, filter="Cuisine*")]
        for className in classes:
            # import the class
            exec("from JumpScale.tools.cuisine.%s.Cuisine%s import *" % (myClassName, className))
            # attach the class to this class
            do = "self.%s=Cuisine%s(self._executor,self._cuisine)" % (className.lower(), className)
            # print(do)
            exec(do)


class JSCuisineFactory:

    def __init__(self):
        self.__jslocation__ = "j.tools.cuisine"
        self._local = None
        self._cuisines_instance = {}
        self.logger = j.logger.get("j.tools.cuisine")

    def _getBaseClass(self):
        return CuisineBase

    def _getBaseAppClass(self):
        return CuisineApp

    def _getBaseClassLoader(self):
        return CuisineBaseLoader

    def reset(self, cuisine):
        """
        reset remove the cuisine instance passed in argument from the cache.
        """
        if cuisine.executor.id in self._cuisines_instance:
            del self._cuisines_instance[cuisine.executor.id]

    @property
    def local(self):
        if self._local is None:
            from JumpScale.tools.cuisine.JSCuisine import JSCuisine
            self._local = JSCuisine(j.tools.executor.getLocal())
        return self._local

    def _generate_pubkey(self):
        if not j.do.checkSSHAgentAvailable():
            j.do._loadSSHAgent()
        rc, out = j.sal.process.execute("ssh-add -l")
        keys = []
        for line in out.split("\n"):
            try:
                # TODO: ugly needs to be done better
                item = line.split(" ", 2)[2]
                keyname = item.split("(", 1)[0].strip()
                keys.append(keyname)
            except:
                pass
        key = j.tools.console.askChoice(keys, "please select key")
        # key = j.sal.fs.getBaseName(key)
        return j.sal.fs.fileGetContents(key + ".pub")

    def get_pubkey(self, keyname=''):
        if keyname == '':
            return self._generate_pubkey()

        key = j.do.getSSHKeyPathFromAgent(keyname)
        return j.sal.fs.fileGetContents(key + '.pub')

    def _get_ssh_executor(self, addr, port, login, passphrase, passwd):
        if not passwd and passphrase is not None:
            return j.tools.executor.getSSHBased(addr=addr,
                                                port=port,
                                                login=login,
                                                passphrase=passphrase)
        else:
            passwd = passwd if passwd else j.tools.console.askPassword("please specify root passwd", False)
            return j.tools.executor.getSSHBased(addr=addr,
                                                port=port,
                                                login=login,
                                                passwd=passwd)

    # UNUSED METHOD
    def authorizeKey(self, addr='localhost:22', login="root", passwd="", keyname="", pubkey="", passphrase=None):
        """
        will try to login if not ok then will try to push key with passwd
        will push local key to remote, if not specified will list & you can select

        if passwd not specified will ask

        @param pubkey is the pub key to use (is content of key), if this is specified then keyname not used & ssh-agent neither
        """
        if addr.find(":") != -1:
            addr, port = addr.split(":", 1)
            addr = addr.strip()
            port = int(port.strip())
        else:
            port = 22

        j.clients.ssh.cache = {}  # Empty the cache

        _pubkey = pubkey if pubkey else self.get_pubkey(keyname=keyname)
        executor = self._get_ssh_executor(addr, port, login, passphrase, passwd)
        executor.cuisine.ssh.authorize(login, _pubkey)
        executor.cuisine.core.run("chmod -R 700 /root/.ssh")

    def get(self, executor=None, usecache=True):
        """
        example:
        executor=j.tools.executor.getSSHBased(addr='localhost', port=22,login="root",passwd="1234",pushkey="ovh_install")
        cuisine=j.tools.cuisine.get(executor)

        executor can also be a string like: 192.168.5.5:9022

        or if used without executor then will be the local one
        """
        from JumpScale.tools.cuisine.JSCuisine import JSCuisine
        executor = j.tools.executor.get(executor)

        if usecache and executor.id in self._cuisines_instance:
            return self._cuisines_instance[executor.id]

        cuisine = JSCuisine(executor)
        self._cuisines_instance[executor.id] = cuisine
        return self._cuisines_instance[executor.id]

    def getFromId(self, id):
        executor = j.tools.executor.get(id)
        return self.get(executor)
