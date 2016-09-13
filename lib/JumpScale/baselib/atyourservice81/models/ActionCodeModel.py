from JumpScale import j

from JumpScale.baselib.atyourservice81.models.ModelBase import ModelBase


class ActionCodeModel(ModelBase):
    """
    Object holding source code from service template actions
    """

    @classmethod
    def list(self, actorName="", name="", returnIndex=False):
        if name == "":
            name = ".*"
        if actorName == "":
            actorName = ".*"
        regex = "%s:%s" % (actorName, name)
        return self._index.list(regex, returnIndex=returnIndex)

    @classmethod
    def find(self, actorName="", name=""):
        res = []
        for key in self.list(actorName, name):
            res.append(self._modelfactory.get(key))
        return res

    def index(self):
        # put indexes in db as specified
        ind = "%s:%s" % (self.dbobj.actorName, self.dbobj.name)
        self._index.index({ind: self.key})

    def _post_init(self):
        pass

    def _pre_save(self):
        pass

    def argAdd(self, name, defval=""):
        """
        name @0: Text;
        defval @1: Data;
        """
        for item in self.dbobj.args:
            if item.name == name:
                item.defval = defval
                return
        obj = self.argumentNewObj()
        obj.name = name
        obj.defval = defval
        return obj

    def argumentNewObj(self):
        olditems = [item.to_dict() for item in self.dbobj.args]
        newlist = self.dbobj.init("args", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        ooo = newlist[-1]
        return ooo
