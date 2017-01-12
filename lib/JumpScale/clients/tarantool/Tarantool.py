from JumpScale import j
import tarantool
# import itertools


# import sys
# sys.path.append(".")
# from tarantool_queue import *

try:
    import tarantool
except:
    rc, out, err = j.sal.process.execute("pip3 install tarantool", die=True, showout=False, ignoreErrorOutput=False)
    import tarantool


class Tarantool():

    def __init__(self, client):
        self.db = client
        self.call = client.call

    # def addSpace(self):
    #     C = "s = box.schema.space.create('tester',{if_not_exists = true})"

    def getQueue(self, name, ttl=0, delay=0):
        return TarantoolQueue(self, name, ttl=ttl, delay=delay)

    def eval(self, code):
        code = j.data.text.strip(code)
        self.db.eval(code)

    def userGrant(self, user="guest", operation=1, objtype="universe", objname=""):
        """
        @param objtype the type of object - "space" or "function" or "universe",
        @param objname the name of object only relevant for space or function
        @param opstype in integer the type of operation - "read" = 1, or "write" = 2, or "execute" = 4, or a combination such as "read,write,execute".
        """
        if objname == "":
            C = "box.schema.user.grant('%s',%s,'%s')" % (user, operation, objtype)
        else:
            C = "box.schema.user.grant('%s',%s,'%s','%s')" % (user, operation, objtype, objname)

        self.db.eval(C)

    def addFunction(self, code=""):
        """
        example:
            function echo3(name)
              return name
            end

        then use with self.call...
        """
        if code == "":
            code = """
            function echo3(name)
              return name
            end
            """
        self.eval(code)


class TarantoolQueue:

    def __init__(self, tarantoolclient, name, ttl=0, delay=0):
        """The default connection parameters are: host='localhost', port=9999, db=0"""
        self.client = tarantoolclient
        self.db = self.client.db
        self.name = name
        if ttl != 0:
            raise RuntimeError("not implemented")
        else:
            try:
                self.db.eval('queue.create_tube("%s","fifottl")' % name)
            except Exception as e:
                if "already exists" not in str(e):
                    raise RuntimeError(e)

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.__db.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize() == 0

    def put(self, item, ttl=None, delay=0):
        """Put item into the queue."""
        args = {}
        if ttl is not None:
            args["ttl"] = ttl
            args["delay"] = delay

        self.db.call("queue.tube.%s:put" % self.name, item, args)
        # else:
        #     #TODO: does not work yet? don't know how to pass
        #     self.db.call("queue.tube.%s:put"%self.name,item)

    def get(self, timeout=1000, autoAcknowledge=True):
        """
        Remove and return an item from the queue.
        if necessary until an item is available.
        """
        res = self.db.call("queue.tube.%s:take" % self.name, timeout)
        if autoAcknowledge and len(res) > 0:
            res = self.db.call("queue.tube.%s:ack" % self.name, res[0])
        return res

    def fetch(self, block=True, timeout=None):
        """ Like get but without remove"""
        if block:
            item = self.__db.brpoplpush(self.key, self.key, timeout)
        else:
            item = self.__db.lindex(self.key, 0)
        return item

    def set_expire(self, time):
        self.__db.expire(self.key, time)

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(False)


class TarantoolFactory:

    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.tarantool"
        self._tarantool = {}
        self._tarantoolq = {}
        # self._config = {}
        # self._cuisine = j.tools.cuisine.get()

    # def getInstance(self, cuisine):
    #     self._cuisine = cuisine
    #     return self

    def deployRun(self, addr, passwd, port=3333, bootstrap=""):
        """
        @param addr in format myserver:22 or myserver (is the ssh connection)
        @param boostrap can be used to e.g. create a scheme

        default:
                box.once("bootstrap", function()
                    box.schema.space.create('test')
                    box.space.test:create_index('primary',
                        { type = 'TREE', parts = {1, 'NUM'}})
                    box.schema.user.grant('$user', 'read,write,execute', 'universe')
                end)

        """
        cuisine = j.tools.cuisine.get(addr)

        if bootstrap == "":
            bootstrap = """
                    box.once("bootstrap", function()
                        box.schema.space.create('test')
                        box.space.test:create_index('primary',
                            { type = 'TREE', parts = {1, 'NUM'}})
                    end)
                    box.schema.user.grant('$user', 'read,write,execute', 'universe')
                    """

        cuisine.fw.allowIncoming(port)

        cuisine.core.run("apt-get install tarantool -y")

        LUA = """
        box.cfg{listen = $port}
        box.schema.user.create('admin', {if_not_exists = true,password = '$passwd'})
        box.schema.user.passwd('admin','$passwd')
        require('console').start()
        """
        LUA = LUA.replace("$passwd", passwd)
        LUA = LUA.replace("$port", str(port))

        luapath = cuisine.core.replace("$TMPDIR/tarantool.lua")

        print("write lua startup to:%s" % luapath)

        cuisine.core.file_write(luapath, LUA)

        cuisine.tmux.createWindow("zconfig", "tarantool")

        cuisine.tmux.executeInScreen("zconfig", "tarantool",
                                     "cd $TMPDIR;rm -rf tarantool;mkdir tarantool;cd tarantool;tarantool %s" % luapath, replaceArgs=True)

    def get(self, ipaddr="localhost", port=3301, login="guest", password=None, fromcache=True):
        key = "%s_%s" % (ipaddr, port)
        if key not in self._tarantool or fromcache is False:
            self._tarantool[key] = tarantool.connect(ipaddr, user=login, port=port, password=password)
        return Tarantool(self._tarantool[key])

    def test(self):
        C = """
        function echo3(name)
          return name
        end
        """
        tt = self.get("192.168.99.100", 3301)
        tt.eval(C)
        print("return:%s" % tt.call("echo3", "testecho"))
