from JumpScale import j

from collections import OrderedDict


class ModelBase():

    def __init__(self, modelfactory, key="", new=False):
        self.logger = j.atyourservice.logger
        self._modelfactory = modelfactory
        self._capnp = modelfactory._capnp
        self._category = modelfactory.category
        self._db = modelfactory._db
        self._index = modelfactory._index
        self._key = ""
        if key != "":
            if len(key) != 16 and len(key) != 32:
                raise j.exceptions.Input("Key needs to be length 32")

        if new:
            self.dbobj = self._capnp.new_message()
            self._post_init()
            if key != "":
                self._key = key
        elif key != "":
            # will get from db
            if self._db.exists(key):
                self.load(key=key)
            else:
                raise j.exceptions.Input(message="Cannot find object:%s!%s" % (
                    modelfactory.category, key), level=1, source="", tags="", msgpub="")
        else:
            raise j.exceptions.Input(message="key cannot be empty when no new obj is asked for.",
                                     level=1, source="", tags="", msgpub="")

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
        buff = self._db.get(key)
        self.dbobj = self._capnp.from_bytes(buff, builder=True)

    def save(self):
        self._pre_save()
        buff = self.dbobj.to_bytes()
        self._db.set(self.key, buff)
        self.index()

    @property
    def dictFiltered(self):
        """
        remove items from obj which cannot be serialized to json or not relevant in dict
        """
        return self.dbobj.to_dict()

    @property
    def dictJson(self):
        ddict2 = OrderedDict(self.dictFiltered)
        return j.data.serializer.json.dumps(ddict2, sort_keys=True, indent=True)

    def __repr__(self):
        return self.dictJson

    __str__ = __repr__


class ModelBaseWithData(ModelBase):

    @property
    def data(self):
        return j.data.capnp.getObj(self.dbobj.dataSchema, binaryData=self.dbobj.data)

    @property
    def dataSchema(self):
        return j.data.capnp.getSchema(self.dbobj.dataSchema)

    @property
    def dataJSON(self):
        return j.data.capnp.getJSON(self.data)

    @property
    def dataBinary(self):
        return j.data.capnp.getBinaryData(self.data)
