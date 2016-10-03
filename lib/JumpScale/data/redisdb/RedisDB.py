from JumpScale import j
import time


class RedisDB:

    def __init__(self):
        self.__jslocation__ = "j.data.redisdb"

    def get(self, path, expiration=None):
        """
        @param path in form of someting:something:...

        TODO: *2 please describe and give example

        """
        return RedisDBList(path, expiration)

    def _test(self):
        llist = self.get("root1:child1")

        llist.delete()
        data = {"a": "b"}
        llist.set(data, "akey")

        print("iterator:")
        counter = 0
        for item in llist:
            counter += 1
            print(item)
        print("did you see 1 item")

        assert(counter == 1)

        assert data == llist.get("akey").struct
        assert llist.len() == 1
        llist.set(data, "akey")

        assert llist.len() == 1
        llist.set(data, "akey2")
        assert llist.len() == 2
        llist.delete()
        # now tests around id
        for i in range(10):
            data = {"a": "b", "id": str(i), "aval": i}
            llist.set(data, "akey%s" % i)

        print(llist.get(id="5"))

        res = llist.find(id="5")

        assert len(res) == 1

        res = llist.find(id="5")
        assert res[0].struct["id"] == "5"

        res = llist.find(aval=5)
        assert len(res) == 1


class RedisDBObj:

    def __init__(self, llist, path, id=""):
        self._list = llist
        self.db = j.core.db
        self.path = path
        self._struct = {}
        self._id = id

    @property
    def id(self):
        if self._id == "":
            self._id = self.struct["id"]
        return self._id

    @property
    def struct(self):
        data = self.db.hget(self.path, self.id)
        if data is None:
            raise j.exceptions.RuntimeError(
                "could not find object %s:%s" % (self.path, self.id))
        obj = j.data.serializer.json.loads(data)
        if "id" in obj:
            self._id = obj["id"]
        return obj

    @struct.setter
    def struct(self, val):
        if j.data.types.dict.check(val) is False:
            raise j.exceptions.RuntimeError("only dict supported")
        self.db.hset(self.path, self.id,
                     j.data.serializer.json.dumps(val, sort_keys=True))
        if self._list._expiration:
            self.db.expire(self.path, self._list._expiration)
        else:
            self._list._list = {}  # will reload

    def __repr__(self):
        return j.data.serializer.json.dumps(self.struct, sort_keys=True, indent=True)

    __str__ = __repr__


class RedisDBList:

    def __init__(self, path, expiration=None):
        self.db = j.core.db
        self.path = path
        self._list = {}
        self._expiration = expiration

    @property
    def list(self):
        if self._expiration or not self._list:
            keys = sorted(self.db.hkeys(self.path))
            for name in keys:
                self._list[name] = RedisDBObj(self, self.path, name)
        keys = sorted(self._list.keys())
        res = []
        for key in keys:
            res.append(self._list[key])
        return res

    def exists(self, id):
        return self.db.hexists(self.path, id)

    def get(self, id):
        obj = RedisDBObj(self, self.path, id)
        return obj

    def set(self, data, id=""):
        if j.data.types.dict.check(data) is False:
            raise j.exceptions.RuntimeError("only dict supported")
        if not id:
            id = data['id']
        obj = RedisDBObj(self, self.path, id)
        obj.struct = data
        self._list = {}
        return obj

    def find(self, **filter):
        res = []
        for item in self.list:
            if id and item.id != id:
                continue
            found = True
            for key, val in filter.items():
                if item.struct[key] != val:
                    found = False
                    break
            if found:
                res.append(item)
        return res

    def delete(self):
        self.db.delete(self.path)
        self._list = {}

    def remove(self, id):
        self.db.hdel(self.path, id)
        self._list.pop(id, None)

    def __iter__(self):
        return self.list.__iter__()

    def len(self):
        if self._expiration:
            return self.db.hlen(self.path)
        else:
            return len(self.list)

    def __bool__(self):
        return self.len() != 0

    def __repr__(self):
        out = ""
        for item in self.list:
            out += "%s %s\n" % (self.path, item.id)
        if out == "":
            out = "Empty list %s" % (self.path)
        return out

    __str__ = __repr__
