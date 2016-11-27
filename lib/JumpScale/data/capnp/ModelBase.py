from JumpScale import j

from collections import OrderedDict


class ModelBase():

    def __init__(self, capnp_schema, category, db, index, key="", new=False):

        self._capnp_schema = capnp_schema
        self._category = category
        self._db = db
        self._index = index
        self._key = ""
        self.dbobj = None
        self.changed = False

        if key != "":
            if len(key) != 16 and len(key) != 32:
                raise j.exceptions.Input("Key needs to be length 32")

        if new:
            self.dbobj = self._capnp_schema.new_message()
            self._post_init()
            if key != "":
                self._key = key
        elif key != "":
            # will get from db
            if self._db.exists(key):
                self.load(key=key)
                self._key = key
            else:
                raise j.exceptions.Input(message="Cannot find object:%s!%s" % (
                    self._category, key), level=1, source="", tags="", msgpub="")
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

    def index(self):
        # put indexes in db as specified
        ind = "%s" % (self.dbobj.name)
        self._index.index({ind: self.key})

    def load(self, key):
        if self._db.inMem:
            raise RuntimeError("should not get here")
        buff = self._db.get(key)
        self.dbobj = self._capnp_schema.from_bytes(buff, builder=True)

    def save(self):
        self._pre_save()
        if not self._db.inMem:
            # no need to store when in mem because we are the object which does not have to be serialized
            # so this one stores when not mem
            buff = self.dbobj.to_bytes()
            if hasattr(self.dbobj, 'clear_write_flag'):
                self.dbobj.clear_write_flag()
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

    def __init__(self, capnp_schema, category, db, index, key="", new=False):
        super().__init__(capnp_schema=capnp_schema, category=category, db=db, index=index, key=key, new=new)
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = j.data.capnp.getObj(self.dbobj.dataSchema, binaryData=self.dbobj.data)
        return self._data

    @property
    def dataSchema(self):
        return j.data.capnp.getSchema(self.dbobj.dataSchema)

    @property
    def dataJSON(self):
        return j.data.capnp.getJSON(self.data)

    @property
    def dataBinary(self):
        return j.data.capnp.getBinaryData(self.data)


class ModelBaseCollection:
    """
    This class represent a collection
    It's used to list/find/create new Instance of Model objects

    """

    def __init__(self, schema, category, modelBaseClass=None, db=None, indexDb=None):
        """
        @param modelBaseClass, important to pass the class not the object
        """

        self.category = category
        namespace = self.category
        self.capnp_schema = schema

        if db == None:
            self._db = j.servers.kvs.getMemoryStore(name=namespace, namespace=namespace)
        else:
            self._db = db
        if indexDb == None:
            # for now we do index same as database
            self._index = self._db
        else:
            self._index = indexDb

        if not modelBaseClass == None:
            self.modelBaseClass = modelBaseClass
        else:
            self.modelBaseClass = ModelBase

    def new(self):
        model = self.modelBaseClass(
            capnp_schema=self.capnp_schema,
            category=self.category,
            db=self._db,
            index=self._index,
            key='',
            new=True)

        if self._db.inMem:
            self._db.db[model.key] = model

        return model

    def get(self, key):
        if self._db.inMem:
            if key in self._db.db:
                model = self._db.db[key]
            else:
                raise j.exceptions.Input(message="Could not find key:%s for model:%s" %
                                         (key, self.category), level=1, source="", tags="", msgpub="")
        else:
            model = self.modelBaseClass(
                capnp_schema=self.capnp_schema,
                category=self.category,
                db=self._db,
                index=self._index,
                key=key,
                new=False)
        return model

    def list(self, name="", state=None):
        """
        @param name can be the full name e.g. node.ssh or a rule but then use e.g. node.*  (are regexes, so need to use .* at end)
        @param state
            new
            ok
            error
            disabled
        """
        if name == "":
            name = ".*"
        if state == "":
            state = ".*"
        if state != None and name != None:
            regex = "%s:%s" % (name, state)
        elif name != None:
            regex = "%s" % (name)
        elif state != None:
            regex = "%s" % (state)
        else:
            regex = ".*"
        res = self._index.list(regex)
        return res

    def find(self, name="", state=None):
        """
        @param name can be the full name e.g. node.ssh or a rule but then use e.g. node.*  (are regexes, so need to use .* at end)
        @param state
            new
            ok
            error
            disabled
        """
        res = []
        for key in self.list(name=name, state=state):
            res.append(self.get(key))
        return res

    def destroy(self):
        self._db.destroy()
        self._index.destroy()
