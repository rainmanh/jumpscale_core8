
from JumpScale import j
import sys
import os

from collections import OrderedDict
from ModelBase import ModelBase, ModelBaseWithData


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
        # . are removed from . to Uppercase
        args = args.copy()  # to not change the args passed in argument
        for key in list(args.keys()):
            sanitize_key = j.data.hrd.sanitize_key(key)
            if key != sanitize_key:
                args[sanitize_key] = args[key]
                args.pop(key)

        schema = self.getSchema(schemaInText)
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

    def getJSON(self, obj):
        configdata2 = obj.to_dict()
        ddict2 = OrderedDict(configdata2)
        return j.data.serializer.json.dumps(ddict2, sort_keys=True, indent=True)

    def getBinaryData(self, obj):
        return obj.to_bytes_packed()
