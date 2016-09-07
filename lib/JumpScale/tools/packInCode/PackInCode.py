
from JumpScale import j

    as json


class packInCodeFactory:

    def __init__(self):
        self.__jslocation__ = "j.tools.packInCode"

    def get4python(self):
        return packInCodePython()


class packInCodePython:

    def __init__(self):
        self.code = """
from JumpScale import j
import JumpScale.tools.packInCode
codegen=j.tools.packInCode.get4python()

"""

    def _serialize(self, c):
        c = c.replace("\"", "\\\"")
        return c

    def unserialize(self, c):
        c = c.replace("\\\"", "\"")
        return c

    def addBlock(self, name, block):
        C = """
$name=\"\"\"
$block
\"\"\"

"""
        C = C.replace("$block", self._serialize(block))
        C = C.replace("$name", name)
        self.code += C

    def addDict(self, name, ddict):
        code = j.data.serializer.json.dumps(obj=ddict, sort_keys=True, indent=4, separators=(',', ': '))
        self.code += "%s=\"\"\"\n%s\n\"\"\"\n\n" % (name, code)

    def addHRD(self, name, hrd):
        C = """
hrdtmp=\"\"\"
$hrd
\"\"\"
hrdtmp=codegen.unserialize(hrdtmp)
$name=j.data.hrd.get(content=hrdtmp)
"""
        C = C.replace("$name", name)
        C = C.replace("$hrd", self._serialize(str(hrd)))
        self.code += "%s\n" % C

    def addPyFile(self, path2add, path2save=None):
        if path2save is None:
            path2save = path2add
        code = j.sal.fs.fileGetContents(path2add)
        C = """
codetmp=\"\"\"
$code
\"\"\"
j.sal.fs.createDir(j.sal.fs.getParent(\"$path2save\"))
codetmp=codegen.unserialize(codetmp)
j.sal.fs.writeFile(\"$path2save\",codetmp)
"""
        C = C.replace("$code", self._serialize(code))
        C = C.replace("$path2save", str(path2save))
        self.code += "%s\n" % C

    def save(self, path):
        j.sal.fs.writeFile(path, self.code)

    def get(self):
        return self.code
