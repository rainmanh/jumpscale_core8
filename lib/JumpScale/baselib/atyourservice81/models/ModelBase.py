from JumpScale import j


class ModelBase():

    def __init__(self, modelfactory, key=""):
        self.logger = j.atyourservice.logger
        self._modelfactory = modelfactory
        self._capnp = modelfactory._capnp
        self._category = modelfactory.category
        self._db = modelfactory._db
        self._index = modelfactory._index
        self._key = ""
        if key != "" and self._db.exists(key):
            # will get from db
            self.load(key=key)
        else:
            self.dbobj = self._capnp.new_message()
            self._post_init()

    @property
    def key(self):
        if self._key == "":
            self._key = self._generate_key()
        return self._key

    def _post_init(self):
        pass

    def _pre_save(self):
        # needs to be implemented see e.g. ActorModel
        pass

    def _generate_key(self):
        # return a unique key to be used in db (std the key but can be overriden)
        return j.data.hash.md5_string(j.data.idgenerator.generateGUID())

    @classmethod
    def list(**args):
        raise NotImplemented

    @classmethod
    def find(**args):
        raise NotImplemented

    def index(self):
        # put indexes in db as specified
        raise NotImplemented

    def load(self, key):
        """
        please do not use key when loading, will use predefined one, only relevant in init
        """
        buff = self._db.get(key)
        self.dbobj = self._capnp.from_bytes(buff, builder=True)

    def save(self):
        self._pre_save()
        buff = self.dbobj.to_bytes()
        self._db.set(self.key, buff)
        self.index()

    def __repr__(self):
        ddict = self.dbobj.to_dict()
        # ddict = sortedcontainers.SortedDict(ddict)
        return j.data.serializer.json.dumps(ddict, True, True)

    __str__ = __repr__
