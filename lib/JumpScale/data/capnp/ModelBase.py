from JumpScale import j

from collections import OrderedDict


class ModelBase():

    def __init__(self, key="", new=False, collection=None):

        self._propnames = []
        self.collection = collection
        self.logger = collection.logger

        self._key = ""

        self.dbobj = None
        self.changed = False
        self._subobjects = {}

        if j.data.types.bytes.check(key):
            key = key.decode()

        # if key != "":
        #     if len(key) != 16 and len(key) != 32 and len(key) != 64:
        #         raise j.exceptions.Input("Key needs to be length 16,32,64")

        if new:
            self.collection.logger.debug("new:%s" % key)
            self.dbobj = self.collection.capnp_schema.new_message()
            self._post_init()
            if key != "":
                self._key = key
        elif key != "":
            # will get from db
            if self.collection_db.exists(key):
                self.collection.logger.debug("exists:%s" % key)
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
        self.collection._index.index({self.dbobj.name: self.key})

    def load(self, key):
        if self.collection._db.inMem:
            raise RuntimeError("when using in memory store it should not try to load")

        buff = self.collection._db.get(key)
        self.dbobj = self.collection.capnp_schema.from_bytes(buff, builder=True)

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

    # def __dir__(self):
    #     propnames = ["key", "index", "load", "_post_init", "_pre_save", "_generate_key", "save", "logger",
    #                  "dictFiltered", "reSerialize", "dictJson", "raiseError", "addSubItem", "_listAddRemoveItem",
    #                  "logger", "_capnp_schema", "_category", "_db", "_index", "_key", "dbobj", "changed", "_subobjects"]
    #     return propnames + self._propnames

    def reSerialize(self):
        toRemove = []
        for key, item in self._subobjects.items():
            prop = self.__dict__["list_%s" % key]
            dbobjprop = eval("self.dbobj.%s" % key)
            if len(dbobjprop) != 0:
                raise RuntimeError("bug, dbobj prop should be empty, means we didn't reserialize properly")
            if len(prop) > 0:
                # init the subobj, iterate over all the items we have & insert them
                subobj = self.dbobj.init(key, len(prop))
                for x in range(0, len(prop)):
                    subobj[x] = prop[x]
            toRemove.append(key)

        # cannot do above because still iterating
        for key in toRemove:
            self._subobjects.pop(key)
            self.__dict__.pop("list_%s" % key)

    def save(self):
        self._pre_save()
        self.reSerialize()
        if self.collection._db.inMem:
            self.collection._db.db[self.key] = self
        else:
            # no need to store when in mem because we are the object which does not have to be serialized
            # so this one stores when not mem
            buff = self.dbobj.to_bytes()
            if hasattr(self.dbobj, 'clear_write_flag'):
                self.dbobj.clear_write_flag()
            self.collection._db.set(self.key, buff)
        self.index()

    def to_dict(self):
        self.reSerialize()
        d = self.dbobj.to_dict()
        d['key'] = self.key
        return d

    @property
    def dictFiltered(self):
        """
        remove items from obj which cannot be serialized to json or not relevant in dict
        """
        # made to be overruled
        return self.to_dict()

    @dictFiltered.setter
    def dictFiltered(self, ddict):
        """
        """
        if "key" in ddict:
            self.key = ddict[key]
        self.dbobj = self.collection.capnp_schema.new_message(**ddict)

    @property
    def dictJson(self):
        ddict2 = OrderedDict(self.dictFiltered)
        return j.data.serializer.json.dumps(ddict2, sort_keys=True, indent=True)

    def raiseError(self, msg):
        msg = "Error in dbobj:%s (%s)\n%s" % (self._category, self.key, msg)
        raise j.exceptions.Input(message=msg, level=1, source="", tags="", msgpub="")

    def addSubItem(self, name, data):
        """
        @param data is string or object first retrieved by self.collection.list_$name_constructor(**args)
        can also directly add them to self.list_$name.append(self.collection.list_$name_constructor(**args)) if it already exists
        """
        self._listAddRemoveItem(name=name)
        self.__dict__["list_%s" % name].append(data)

    def initSubItem(self, name):
        self._listAddRemoveItem(name=name)

    def deleteSubItem(self, name, pos):
        """
        @param pos is the position in the list
        """
        self._listAddRemoveItem(name=name)
        self.__dict__["list_%s" % name].pop(pos)

    def _listAddRemoveItem(self, name):
        """
        if you want to change size of a list on obj use this method
        capnp doesn't allow modification of lists, so when we want to change size of a list then we need to reSerialize
        and put content of a list in a python list of dicts
        we then re-serialize and leave the subobject empty untill we know that we are at point we need to save the object
        when we save we populate the subobject so we get a nicely created capnp message
        """
        if name in self._subobjects:
            # means we are already prepared
            return
        prop = eval("self.dbobj.%s" % name)
        if len(prop) == 0:
            self.__dict__["list_%s" % name] = []
        else:
            self.__dict__["list_%s" % name] = [item for item in prop]

        # empty the dbobj list
        exec("self.dbobj.%s=[]" % name)

        self._subobjects[name] = True
        self.changed = True

    def __repr__(self):
        out = "key:%s\n" % self.key
        out += self.dictJson
        return out

    __str__ = __repr__


class ModelBaseWithData(ModelBase):

    def __init__(self, capnp_schema, category, db, index, key="", new=False, collection=None):
        super().__init__(capnp_schema=capnp_schema, category=category, db=db, index=index, key=key, new=new, collection=collection)
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


def getText(text):
    return str(object=text)


def getInt(nr):
    return int(nr)


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
            # pass this to the constructor.
            ModelCapnp.MyStruct
        @param category str: category of the model. need to be the same as the category of the single model class
        @param namespace: namespace used to store these object in key-value store
        @param modelBaseClass: important to pass the class not the object. Class used to create instance of this category.
                               Need to inherits from JumpScale.data.capnp.ModelBase.ModelBalse
        @param db: connection object to the key-value store
        @param indexDb: connection object to the key-value store used for indexing
        """

        self.category = category
        self.namespace = namespace if namespace else category
        self.capnp_schema = schema

        self.propnames = [item for item in self.capnp_schema.schema.fields.keys()]

        self._listConstructors = {}

        for field in self.capnp_schema.schema.fields_list:
            try:
                str(field.schema)
            except:
                continue

            if "List" in str(field.schema):
                slottype = str(field.proto.slot.type).split("(")[-1]
                if slottype.startswith("text"):
                    # is text
                    self._listConstructors[field.proto.name] = getText
                elif slottype.startswith("uint"):
                    # is text
                    self._listConstructors[field.proto.name] = getInt
                else:
                    subTypeName = str(field.schema.elementType).split(".")[-1].split(">")[0]
                    self._listConstructors[field.proto.name] = eval("self.capnp_schema.%s.new_message" % subTypeName)

                self.__dict__["list_%s_constructor" % field.proto.name] = self._listConstructors[field.proto.name]

        self._db = db if db else j.servers.kvs.getMemoryStore(name=self.namespace, namespace=self.namespace)
        # for now we do index same as database
        self._index = indexDb if indexDb else self._db

        self.modelBaseClass = modelBaseClass if modelBaseClass else ModelBase

        self.logger = j.logger.get("modelBase_%s" % category)
        self.logger.debug("initted.")

    @property
    def objType(self):
        return self.capnp_schema.schema.node.displayName

    def new(self, key=""):
        model = self.modelBaseClass(key=key, new=True, collection=self)
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
                new=autoCreate,
                collection=self)
        return model

    def list(self, name="", returnIndex=False):
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
        regex = name
        res = self._index.list(regex, returnIndex=returnIndex)
        return res

    def find(self, name=""):
        """
        @param name can be the full name e.g. node.ssh or a rule but then use e.g. node.*  (are regexes, so need to use .* at end)
        @param state
            new
            ok
            error
            disabled
        """
        res = []
        for key in self.list(name=name):
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
