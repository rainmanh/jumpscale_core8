
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class DirModel(base):
    """
    Model Class for an Issue object
    """

    def index(self):
        ind = "%s" % (self.dbobj.location)
        self._index.index({ind: self.key})

    def fileExists(self, name):
        return not self.fileGet(name, False) == None

    def fileSpecialExists(self, name):
        return not self.fileSpecialGet(name, False) == None

    def linkExists(self, name):
        return not self.fileSpecialGet(name, False) == None

    def fileGet(self, name):
        for obj in self.dbobj.files:
            if name == obj.name:
                return obj
        return None

    def filesNew(self, nr):
        newlist = self.dbobj.init("files", nr)
        return newlist

    def getTypeId(self):
        pass
        # if S_ISSOCK(value):
        #     self.data[6] = 0
        #
        # elif S_ISLNK(value):
        #     self.data[6] = 1
        #
        # elif S_ISBLK(value):
        #     self.data[6] = 3
        #
        # elif S_ISCHR(value):
        #     self.data[6] = 5
        #
        # elif S_ISFIFO(value):
        #     self.data[6] = 6
        #
        # # keep track of empty directories
        # elif S_ISDIR(value):
        #     self.data[6] = 4

    def setParent(self, parentObj):
        self.dbobj.parent = parentObj.key

    @property
    def dictFiltered(self):
        ddict = self.dbobj.to_dict()
        for item in ddict["specials"]:
            if "data" in item:
                item["data"] = binascii.hexlify(item["data"])
        return ddict

    @dictFiltered.setter
    def dictFiltered(self, ddict):
        for item in ddict["specials"]:
            if "data" in item:
                item["data"] = binascii.unhexlify(item["data"])
        self.dbobj = self._capnp_schema.new_message(**ddict)
        for item in self.dbobj.specials:
            item.data = b"%s" % item.data

    def _pre_save(self):
        pass