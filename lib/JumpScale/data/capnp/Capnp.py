
from JumpScale import j
import sys
import os
import capnp
from collections import OrderedDict
from ModelBase import *


class Capnp:
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.data.capnp"
        self._cache = {}
        self._capnpVarDir = j.sal.fs.joinPaths(j.dirs.VARDIR, "capnp")
        j.sal.fs.createDir(self._capnpVarDir)
        if self._capnpVarDir not in sys.path:
            sys.path.append(self._capnpVarDir)

    def getModelBaseClass(self):
        return ModelBase

    def getModelBaseClassWithData(self):
        return ModelBaseWithData

    def getModelBaseClassCollection(self):
        return ModelBaseCollection

    def getModelCollection(self, schema, category, namespace=None, modelBaseClass=None,
                           modelBaseCollectionClass=None, db=None, indexDb=None):
        """
        @param schema is capnp_schema

        example to use:
            ```
            #if we use a modelBaseClass do something like
            ModelBaseWithData = j.data.capnp.getModelBaseClass()
            class MyModelBase(ModelBaseWithData):
                def producerNewObj(self):
                    olditems = [item.to_dict() for item in self.dbobj.producers]
                    newlist = self.dbobj.init("producers", len(olditems) + 1)
                    for i, item in enumerate(olditems):
                        newlist[i] = item
                    return newlist[-1]

            def index(self):
                # put indexes in db as specified
                ind = "%s" % (self.dbobj.path)
                self._index.index({ind: self.key})


            import capnp
            #there is model.capnp in $libdir/JumpScale/tools/issuemanager
            from JumpScale.tools.issuemanager import model as ModelCapnp

            mydb=j.servers.kvs.getMemoryStore(name="mymemdb")

            collection=j.data.capnp.getModelCollection(schema=ModelCapnp,category="issue",modelBaseClass=MyModelBase,db=mydb,indexDb=mydb)

            ```
        """
        if modelBaseCollectionClass == None:
            modelBaseCollectionClass = ModelBaseCollection

        return modelBaseCollectionClass(schema=schema, category=category, namespace=namespace, db=db, indexDb=indexDb, modelBaseClass=modelBaseClass)

    def getId(self, schemaInText):
        id = [item for item in schemaInText.split("\n") if item.strip() != ""][0][3:-1]
        return id

    def getSchemas(self, schemaInText):
        schemaInText = j.data.text.strip(schemaInText)
        schemaInText = schemaInText.strip() + "\n"
        schemaId = self.getId(schemaInText)
        if schemaId not in self._cache:
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

            # cl = eval("schema_%s" % schemaId + ".schema")
            cl = eval("schema_%s" % schemaId)
            self._cache[schemaId] = cl
        return self._cache[schemaId]

    def getSchemaFromText(self, schemaInText, name="Schema"):
        schemas = self.getSchemas(schemaInText)
        schema = eval("schemas.%s" % name)
        return schema

    def getSchemaFromPath(self, path, name):
        """
        @param path is path to schema
        """
        # need to check if dirname of path is in sys.path
        # load the schema
        # return the schema
        #@TODO *1

    def getObj(self, schemaInText, name="Schema", args={}, binaryData=None):

        # . are removed from . to Uppercase
        args = args.copy()  # to not change the args passed in argument
        for key in list(args.keys()):
            sanitize_key = j.data.hrd.sanitize_key(key)
            if key != sanitize_key:
                args[sanitize_key] = args[key]
                args.pop(key)

        schema = self.getSchemaFromText(schemaInText, name=name)

        if binaryData is not None and binaryData != b'':
            configdata = schema.from_bytes_packed(binaryData).as_builder()
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

    def test(self):
        import time
        capnpschema = '''
        @0x93c1ac9f09464fc9;

        struct Issue {

          state @0 :State;
          enum State {
            new @0;
            ok @1;
            error @2;
            disabled @3;
          }

          #name of actor e.g. node.ssh (role is the first part of it)
          name @1 :Text;

        }
        '''

        # dummy test, not used later
        obj = self.getObj(capnpschema, name="Issue")
        obj.state = "ok"

        # now we just get the capnp schema for this object
        schema = self.getSchemaFromText(capnpschema, name="Issue")

        # mydb = j.servers.kvs.getRedisStore(name="mymemdb")
        mydb = None  # is memory

        collection = self.getModelCollection(schema, category="test", modelBaseClass=None, db=mydb, indexDb=mydb)
        start = time.time()
        print("start populate 100.000 records")
        for i in range(100000):
            obj = collection.new()
            obj.dbobj.name = "test%s" % i
            obj.save()

        print("population done")
        end_populate = time.time()
        print(collection.find(name="test8639"))
        end_find = time.time()
        print("population in %.2fs" % (end_populate - start))
        print("find in %.2fs" % (end_find - end_populate))

    def testWithRedis(self):
        capnpschema = '''
        @0x93c1ac9f09464fc9;

        struct Issue {

          state @0 :State;
          enum State {
            new @0;
            ok @1;
            error @2;
            disabled @3;
          }

          #name of actor e.g. node.ssh (role is the first part of it)
          name @1 :Text;

        }
        '''
        # mydb = j.servers.kvs.getRedisStore("test")
        mydb = j.servers.kvs.getRedisStore(name="test", unixsocket="%s/redis.sock" % j.dirs.TMPDIR)
        schema = self.getSchemaFromText(capnpschema, name="Issue")
        collection = self.getModelCollection(schema, category="test", modelBaseClass=None, db=mydb, indexDb=mydb)
        for i in range(100):
            obj = collection.new()
            obj.dbobj.name = "test%s" % i
            obj.save()
        print(collection.list())

    def getJSON(self, obj):
        configdata2 = obj.to_dict()
        ddict2 = OrderedDict(configdata2)
        return j.data.serializer.json.dumps(ddict2, sort_keys=True, indent=True)

    def getBinaryData(self, obj):
        return obj.to_bytes_packed()
