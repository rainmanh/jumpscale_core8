
from JumpScale import j
import sys
# import capnp
from collections import OrderedDict
from ModelBase import ModelBase, ModelBaseWithData


class ModelFactory():

    def __init__(self, parentfactory, category, classItem):
        self.category = category
        namespace = "%s:%s" % (parentfactory.namespacePrefix, self.category.lower())
        self._db = j.servers.kvs.getRedisStore(namespace, namespace, changelog=False)
        # for now we do index same as database
        self._index = j.servers.kvs.getRedisStore(namespace, namespace, changelog=False)
        self._modelClass = classItem  # eval(self.category + "Model." + self.category + "Model")
        self._capnp = eval("parentfactory.capnpModel." + self.category)
        self.list = self._modelClass.list
        self.find = self._modelClass.find

        # on class level we need relation to _index & _modelfactory
        self._modelClass._index = self._index
        self._modelClass._modelfactory = self

        self.exists = self._db.exists
        self.queueSize = self._db.queueSize
        self.queuePut = self._db.queuePut
        self.queueGet = self._db.queueGet
        self.queueFetch = self._db.queueFetch

    def new(self, key=""):
        model = self._modelClass(modelfactory=self, key=key, new=True)
        return model

    def get(self, key):
        model = self._modelClass(modelfactory=self, key=key)
        return model

    def destroy(self):
        self._db.destroy()
        self._index.destroy()

    def __str__(self):
        return("modelfactory:%s" % (self.category))

    __repr__ = __str__


class Capnp:
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.data.capnp"
        self._cache = {}
        self._capnpVarDir = j.sal.fs.joinPaths(j.dirs.varDir, "capnp")
        j.sal.fs.createDir(self._capnpVarDir)
        if self._capnpVarDir not in sys.path:
            sys.path.append(self._capnpVarDir)

    def getModelFactoryClass(self):
        return ModelFactory

    def getModelBaseClass(self):
        return ModelBase

    def getModelBaseClassWithData(self):
        return ModelBaseWithData

    def getId(self, schemaInText):
        id = [item for item in schemaInText.split("\n") if item.strip() != ""][0][3:-1]
        return id

    def getSchema(self, schemaInText):
        schemaInText = schemaInText.strip() + "\n"
        schemaId = self.getId(schemaInText)
        if schemaId not in self._cache:
            print("load schema:%s" % schemaId)
            nameOnFS = "schema_%s.capnp" % (schemaId)
            path = j.sal.fs.joinPaths(self._capnpVarDir, nameOnFS)
            j.sal.fs.writeFile(filename=path, contents=schemaInText, append=False)
            try:
                cmd = "import schema_%s_capnp as schema_%s" % (schemaId, schemaId)
                exec(cmd)
            except Exception as e:
                if str(e).find("invalid syntax") != -1:
                    raise j.exceptions.Input(message="Could not import schema:%s\n%s\n\nschema:\n%s\npath:%s\nimportcmd:%s\n" %
                                             (schemaId, e, schemaInText, path, cmd), level=1, source="", tags="", msgpub="")
                raise e

            cl = eval("schema_%s" % schemaId + ".Schema")

            self._cache[schemaId] = cl
        return self._cache[schemaId]

    def getObj(self, schemaInText, args={}, binaryData=None):
        #. are removed from . to Uppercase
        for key, val in args.items():
            if "." in key:
                pre, post = key.split(".", 1)
                key2 = pre + post[0].upper() + post[1:]
                args[key2] = args[key]
                args.pop(key)
        schema = self.getSchema(schemaInText)
        if binaryData is not None:
            configdata = schema.from_bytes_packed(binaryData)
        else:
            try:
                configdata = schema.new_message(**args)
            except Exception as e:
                if str(e).find("has no such member") != -1:
                    msg = "cannot create data for schema from arguments, property missing\n"
                    msg += "arguments:\n%s\n" % j.data.serializer.json.dumps(args, sort_keys=True, indent=True)
                    msg += "schema:\n%s" % schemaInText
                    ee = str(e).split("stack:")[0]
                    ee = ee.split("failed:")[1]
                    msg += "capnperror:%s" % ee
                    print(msg)
                    raise j.exceptions.Input(message=msg, level=1, source="", tags="", msgpub="")
                if str(e).find("Value type mismatch") != -1:
                    msg = "cannot create data for schema from arguments, value type mismatch.\n"
                    msg += "arguments:\n%s\n" % j.data.serializer.json.dumps(args, sort_keys=True, indent=True)
                    msg += "schema:\n%s" % schemaInText
                    ee = str(e).split("stack:")[0]
                    ee = ee.split("failed:")[1]
                    msg += "capnperror:%s" % ee
                    print(msg)
                    raise j.exceptions.Input(message=msg, level=1, source="", tags="", msgpub="")
                raise e
        return configdata

    def getJSON(self, obj):
        configdata2 = obj.to_dict()
        ddict2 = OrderedDict(configdata2)
        return j.data.serializer.json.dumps(ddict2, sort_keys=True, indent=True)

    def getBinaryData(self, obj):
        return obj.to_bytes_packed()
