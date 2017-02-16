from JumpScale import j

from collections import OrderedDict
from collections import Mapping


class emptyObject:
    """
    this object is used to keep capnp schema object in memory
    this is lighter then using the capnp object directly
    and it solve the problem of fixed sized list of canpn object
    """

    def __init__(self, u, schema):
        self._schema = schema
        d = self.__dict__
        for k, v in u.items():
            if isinstance(v, Mapping):
                d[k] = emptyObject(v, schema=schema)
            elif isinstance(v, list):
                d[k] = []
                for x in v:
                    if isinstance(x, Mapping):
                        d[k].append(emptyObject(x, schema=schema))
                    else:
                        d[k].append(x)
            else:
                d[k] = u[k]

    def to_dict(self):
        out = {}
        for k, v in self.__dict__.items():
            if isinstance(v, emptyObject):
                out[k] = v.to_dict()
            elif isinstance(v, list):
                out[k] = []
                for x in v:
                    if isinstance(x, emptyObject):
                        out[k].append(x.to_dict())
                    else:
                        out[k].append(x)
            else:
                out[k] = v
        del out['_schema']
        return out

    def to_bytes_packed(self):
        msg = self._schema.new_message(**self.to_dict())
        return msg.to_bytes_packed()

    def to_bytes(self):
        msg = self._schema.new_message(**self.to_dict())
        return msg.to_bytes()

    def __repr__(self):
        return str(self.__dict__)


class ModelBase():

    def __init__(self, capnp_schema, category, db, index, key="", new=False):

        self._propnames = []
        self._capnp_schema = capnp_schema
        self._propnames = [item for item in self._capnp_schema.schema.fields.keys()]

        self.logger = j.logger.get(capnp_schema.schema.node.displayName)  # TODO find something better than this
        self._category = category
        self._db = db
        self._index = index
        self._key = ""
        self.dbobj = None
        self.changed = False
        self._subobjects = {}

        # if key != "":
        #     if len(key) != 16 and len(key) != 32 and len(key) != 64:
        #         raise j.exceptions.Input("Key needs to be length 16,32,64")

        if j.data.types.bytes.check(key):
            key = key.decode()

        if new:
            # create an empty object with the same properties as the capnpn msg
            self.dbobj = j.data.capnp.getMemoryObj(self._capnp_schema)
            self._post_init()
            if key is not None and key != "":
                self._key = key
        elif key != "":
            # will get from db
            if self._db.exists(key):
                self.load(key=key)
                self._key = key
            else:
                raise j.exceptions.NotFound(message="Cannot find object:%s!%s" % (
                    self._category, key), level=1, source="", tags="", msgpub="")
        else:
            raise j.exceptions.Input(message="key cannot be empty when no new obj is asked for.",
                                     level=1, source="", tags="", msgpub="")

    @property
    def key(self):
        if self._key is None or self._key == "":
            self._key = self._generate_key()
        return self._key

    @key.setter
    def key(self, value):
        if j.data.types.bytes.check(value):
            value = value.decode()
        self._key = value

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
        self._index.index({self.dbobj.name: self.key})

    def load(self, key):
        # if self._db.inMem:
        #     raise RuntimeError("when using in memory store it should not try to load")

        buff = self._db.get(key)
        msg = self._capnp_schema.from_bytes(buff)
        self.dbobj = emptyObject(msg.to_dict(verbose=True), self._capnp_schema)

    def __getattr__(self, attr):
        # print("GETATTR:%s" % attr)
        if not attr in self._subobjects:
            self.__dict__[attr] = eval("self.dbobj.%s" % attr)
        return self.__dict__[attr]

    # TODO: *2 would be nice that this works, but can't get it to work, something recursive
    # def __setattr__(self, attr, val):
    #     if attr in ["_propnames", "_subobjects", "dbobj", "_capnp_schema"]:
    #         self.__dict__[attr] = val
    #         print("SETATTRBASE:%s" % attr)
    #         # return ModelBase.__setattr__(self, attr, val)
    #
    #     print("SETATTR:%s" % attr)
    #     if attr in self._propnames:
    #         print("1%s" % attr)
    #         # TODO: is there no more clean way?
    #         dbobj = self._subobjects
    #         print(2)
    #         exec("dbobj.%s=%s" % (attr, val))
    #         print(3)
    #         #
    #     else:
    #         raise j.exceptions.Input(message="Cannot set attr:%s in %s" %
    #                                  (attr, self), level=1, source="", tags="", msgpub="")

    def __dir__(self):
        propnames = ["key", "index", "load", "_post_init", "_pre_save", "_generate_key", "save",
                     "dictFiltered", "reSerialize", "dictJson", "raiseError", "addSubItem", "_listAddRemoveItem",
                     "logger", "_capnp_schema", "_category", "_db", "_index", "_key", "dbobj", "changed", "_subobjects"]
        return propnames + self._propnames

    def save(self):
        self._pre_save()

        if self._db.inMem:
            # no need to store when in mem because we are the object which does not have to be serialized
            self._db.db[self.key] = self
        else:
            # so this one stores when not mem
            msg = self._capnp_schema.new_message(**self.dbobj.to_dict())
            buff = msg.to_bytes()
            self._db.set(self.key, buff)
        self.index()

    @property
    def dictFiltered(self):
        """
        remove items from obj which cannot be serialized to json or not relevant in dict
        """
        d = self.dbobj.to_dict()
        d['key'] = self.key
        return d

    @dictFiltered.setter
    def dictFiltered(self, ddict):
        """
        """
        self.dbobj__.dict__.update(ddict)

    # def reSerialize(self, propertyName=None):
    #     """
    #     will create an empty object & copy all from existing one into the new one to make sure its as dense as possible
    #     """
    #     # print("RESERIALIZE")
    #     if propertyName in self._subobjects:
    #         # means we are already prepared
    #         return
    #     ddict = self.dbobj.to_dict()
    #     if propertyName in ddict:
    #         if propertyName in self.__dict__ and len(self.__dict__[propertyName]) != 0:
    #             raise RuntimeError("bug in reSerialize, this needs to be empty")
    #         self.__dict__[propertyName] = []
    #         prop = eval("self.dbobj.%s" % propertyName)
    #         for item in prop:
    #             self.__dict__[propertyName].append(item)
    #             self._subobjects[propertyName] = True
    #
    #         ddict.pop(propertyName)
    #         # is now a clean obj without the property
    #     self.dbobj = self._capnp_schema.new_message(**ddict)

    @property
    def dictJson(self):
        ddict2 = OrderedDict(self.dictFiltered)
        return j.data.serializer.json.dumps(ddict2, sort_keys=True, indent=True)

    def raiseError(self, msg):
        msg = "Error in dbobj:%s (%s)\n%s" % (self._category, self.key, msg)
        raise j.exceptions.Input(message=msg, level=1, source="", tags="", msgpub="")

        # def addSubItem(self, name, capnpmsg):
        #     self._listAddRemoveItem(name)
        #     self.__dict__[name].append(capnpmsg)
        #     return capnpmsg
        #
        # def _listAddRemoveItem(self, name):
        #     """
        #     if you want to change size of a list on obj use this method
        #     capnp doesn't allow modification of lists, so when we want to change size of a list then we need to reSerialize
        #     and put content of a list in a python list of dicts
        #     we then re-serialize and leave the subobject empty untill we know that we are at point we need to save the object
        #     when we save we populate the subobject so we get a nicely created capnp message
        #     """
        #     if name in self._subobjects:
        #         # means we are already prepared
        #         return
        #     prop = eval("self.dbobj.%s" % name)
        #     if len(prop) == 0:
        #         self._subobjects[name] = True
        #         self.__dict__[name] = []
        #     else:
        #         self.reSerialize(propertyName=name)
        #     self.changed = True

    def __repr__(self):
        out = "key:%s\n" % self.key
        out += self.dictJson
        return out

    __str__ = __repr__


class ModelBaseWithData(ModelBase):

    def __init__(self, capnp_schema, category, db, index, key="", new=False):
        super().__init__(capnp_schema=capnp_schema, category=category, db=db, index=index, key=key, new=new)
        self._data_schema = None
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

    def __init__(self, schema, category, namespace=None, modelBaseClass=None, db=None, indexDb=None):
        """
        @param schema: object created by the capnp librairies after it load a .capnp file.
        example :
            import capnp
            # load the .capnp file
            import model_capnp as ModelCapnp
            # pass this to the constructor as schema.
            ModelBaseCollection(schema=ModelCapnp)

            ModelCapnp.MyStruct
        @param category str: category of the model. need to be the same as the category of the single model class, e.g. issue, actor, user, ...
        @param namespace: namespace used to store these object in key-value store
        @param modelBaseClass: important to pass the class not the object. Class used to create instance of this category.
                               Need to inherits from JumpScale.data.capnp.ModelBase.ModelBalse
        @param db: connection object to the key-value store
        @param indexDb: connection object to the key-value store used for indexing
        """

        self.category = category
        self.namespace = namespace if namespace else category
        self.capnp_schema = schema

        self._db = db if db else j.servers.kvs.getMemoryStore(name=self.namespace, namespace=self.namespace)
        # for now we do index same as database
        self._index = indexDb if indexDb else self._db

        self.modelBaseClass = modelBaseClass if modelBaseClass else ModelBase

    def new(self, key=""):
        model = self.modelBaseClass(
            capnp_schema=self.capnp_schema,
            category=self.category,
            db=self._db,
            index=self._index,
            key=key,
            new=True)

        return model

    def exists(self, key):
        return self._db.exists(key)

    def get(self, key, autoCreate=False):

        if self._db.inMem:
            if key in self._db.db:
                model = self._db.db[key]
            else:
                if autoCreate:
                    return self.new(key=key)
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
                new=autoCreate)
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
        res = self._index.list(regex, returnIndex=True)
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

    def lookupGet(self, name, key):
        return self._index.lookupGet(name, key)

    def lookupSet(self, name, key, fkey):
        """
        @param fkey is foreign key
        """
        return self._index.lookupSet(name, key, fkey)

    def lookupDestroy(self, name):
        return self._index.lookupDestroy(name)
