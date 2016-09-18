import msgpack
from collections import OrderedDict

from JumpScale import j

ModelBase = j.data.capnp.getModelBaseClass()


class ActionModel(ModelBase):
    """
    object which has info required to execute a method (an action)
    """

    @property
    def imports(self):
        return ""

    @property
    def code(self):
        return self.dbobj.code

    @code.setter
    def code(self, val):
        val = val.rstrip() + "\n"
        if "ipshell" in val:
            self.dbobj.debug = True
        elif "from pudb" in val:
            self.dbobj.debug = True
        else:
            self.dbobj.debug = False
        self.dbobj.code = val

    @property
    def args(self):
        if self.dbobj.args == b"":
            return {}
        return msgpack.loads(self.dbobj.args)

    @property
    def argsJons(self):
        ddict2 = OrderedDict(self.args)
        return j.data.serializer.json.dumps(ddict2, sort_keys=True, indent=True)

    @args.setter
    def args(self, val):
        args = msgpack.dumps(val)
        self.dbobj.args = args

    @property
    def key(self):
        if self._key == "":
            self._key = j.data.hash.md5_string(self.dbobj.name + self.dbobj.code)
        return self._key

    @classmethod
    def list(self, origin="", name="", returnIndex=False):
        if name == "":
            name = ".*"
        if origin == "":
            origin = ".*"
        regex = "%s:%s" % (origin, name)
        return self._index.list(regex, returnIndex=returnIndex)

    @classmethod
    def find(self, origin="", name=""):
        res = []
        for key in self.list(origin, name):
            res.append(self._modelfactory.get(key))
        return res

    def index(self):
        # put indexes in db as specified
        ind = "%s:%s" % (self.dbobj.origin, self.dbobj.name)
        self._index.index({ind: self.key})

    def _post_init(self):
        self.dbobj.logStdout = True
        self.dbobj.log = True
        self.dbobj.remember = True

    def _pre_save(self):
        pass

    @property
    def dictFiltered(self):
        ddict = self.dbobj.to_dict()
        if "args" in ddict:
            ddict.pop("args")
        return ddict

    def __repr__(self):
        out = self.dictJson + "\n"
        if self.dbobj.args not in ["", b""]:
            out += "args:\n"
            out += self.argsJons
        return out

    __str__ = __repr__
