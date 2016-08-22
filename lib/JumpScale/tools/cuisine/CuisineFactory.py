from JumpScale import j

import inspect


class CuisineBase:

    def __init__(self, executor, cuisine):
        self._p_cache = None
        self.__classname = None
        self._executor = executor
        self._cuisine = cuisine

    @property
    def _classname(self):
        if self.__classname == None:
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

    def _getBaseClass(self):
        return CuisineBase

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
            from JumpScale.tools.cuisine.Cuisine2 import JSCuisine
            self._local = JSCuisine(j.tools.executor.getLocal())
        return self._local

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

        executor = None
        if not passwd:
            # TODO: fix *1,goal is to test if ssh works, get some weird paramiko issues or timeout is too long
            res = j.clients.ssh.get(addr, port=port, login=login, passwd="", allow_agent=True,
                                    look_for_keys=True, timeout=0.5, key_filename=keyname, passphrase=passphrase, die=False)
            if res is not False:
                executor = j.tools.executor.getSSHBased(
                    addr=addr, port=port, login=login, pushkey=keyname, passphrase=passphrase)
            else:
                passwd = j.tools.console.askPassword("please specify root passwd", False)

        if pubkey == "" and executor is None:
            if keyname == "":
                rc, out = j.sal.process.execute("ssh-add -l")
                keys = []
                for line in out.split("\n"):
                    try:
                        # ugly needs to be done better
                        item = line.split(" ", 2)[2]
                        keyname = item.split("(", 1)[0].strip()
                        keys.append(keyname)
                    except:
                        pass
                key = j.tools.console.askChoice(keys, "please select key")
            else:
                key = keyname
        else:
            key = None

        if executor is None:
            executor = j.tools.executor.getSSHBased(
                addr=addr, port=port, login=login, passwd=passwd, pushkey=key, pubkey=pubkey)

        j.clients.ssh.cache = {}
        executor = j.tools.executor.getSSHBased(addr=addr, port=port, login=login,
                                                pushkey=key)  # should now work with key only

        cuisine = JSCuisine(executor)
        self._cuisines_instance[executor.id] = cuisine
        return self._cuisines_instance[executor.id]

    def get(self, executor=None):
        """
        example:
        executor=j.tools.executor.getSSHBased(addr='localhost', port=22,login="root",passwd="1234",pushkey="ovh_install")
        cuisine=j.tools.cuisine.get(executor)

        executor can also be a string like: 192.168.5.5:9022

        or if used without executor then will be the local one
        """
        from JumpScale.tools.cuisine.Cuisine2 import JSCuisine
        executor = j.tools.executor.get(executor)
        if executor.id in self._cuisines_instance:
            return self._cuisines_instance[executor.id]

        cuisine = JSCuisine(executor)
        self._cuisines_instance[executor.id] = cuisine
        return self._cuisines_instance[executor.id]

    def getFromId(self, id):
        executor = j.tools.executor.get(id)
        return self.get(executor)
