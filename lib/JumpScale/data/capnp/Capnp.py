
from JumpScale import j
import sys
import capnp


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

    def getSchema(self, name, schemaInText):
        name = name.replace(".", "_")
        if not name in self._cache:
            print("load schema:%s" % name)
            md5 = j.data.hash.md5_string(schemaInText)
            nameOnFS = "%s_%s.capnp" % (name, md5)
            path = j.sal.fs.joinPaths(self._capnpVarDir, nameOnFS)
            schemaInText = schemaInText.strip() + "\n"
            j.sal.fs.writeFile(filename=path, contents=schemaInText, append=False)
            try:
                exec("import %s_%s_capnp as %s" % (name, md5, name))
            except Exception as e:
                if str(e).find("invalid syntax") != -1:
                    raise j.exceptions.Input(message="Could not import schema:%s\n%s\n\nschema:\n%s\npath:%s\n\n" %
                                             (name, e, schemaInText, path), level=1, source="", tags="", msgpub="")
                raise e

            cl = eval(name + ".Schema")

            self._cache[name] = cl
        return self._cache[name]
