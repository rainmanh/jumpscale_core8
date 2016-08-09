from JumpScale import j
import tarantool
# import itertools


# import sys
# sys.path.append(".")
# from tarantool_queue import *


class Tarantool():

    def __init__(self, client):
        self.db = client
        self.call = client.call

    def getQueue(self, name, ttl=0, delay=0):
        return TarantoolQueue(self, name, ttl=ttl, delay=delay)

    def eval(self, code):
        code = j.data.text.strip(code)
        self.db.eval(code)


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
                if not "already exists" in str(e):
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
        if ttl != None:
            args["ttl"] = ttl
            args["delay"] = delay

        self.db.call("queue.tube.%s:put" % self.name, item, args)
        # else:
        #     #TODO: does not work yet? don't know how to pass
        #     self.db.call("queue.tube.%s:put"%self.name,item)

    def get(self, timeout=1000, autoAcknowledge=True):
        """Remove and return an item from the queue. 
        if necessary until an item is available."""
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

    def get(self, ipaddr="localhost", port=3301, login="guest", password=None, fromcache=True):
        key = "%s_%s" % (ipaddr, port)
        if key not in self._tarantool or fromcache == False:
            self._tarantool[key] = tarantool.connect(
                ipaddr, port=port, password=password)
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
