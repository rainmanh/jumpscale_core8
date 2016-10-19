import msgpack
from collections import OrderedDict
from JumpScale import j

ModelBase = j.data.capnp.getModelBaseClassWithData()


class RepoModel(ModelBase):
    """
    Model Class for an Repo object
    """ 

    @property
    def path(self):
        return self.dbobj.path

    @path.setter
    def path(self, value):
        self.dbobj.path = value

    @property
    def name(self):
        return j.sal.fs.getBaseName(self.dbobj.path)

    @classmethod
    def list(self, path="", returnIndex=False):
        if path == "":
            path = ".*"
        regex = "%s" % (path)
        return self._index.list(regex, returnIndex=returnIndex)

    def index(self):
        # put indexes in db as specified
        ind = "%s" % (self.dbobj.path)
        self._index.index({ind: self.key})

    @classmethod
    def find(self, path=""):
        res = []
        for key in self.list(path):
            res.append(self._modelfactory.get(key))
        return res

    def delete(self):
        self._db.delete(self.key)
        self._index.index_remove(self.path)

    def objectGet(self):
        """
        returns an Actor object created from this model
        """
        repo = j.atyourservice._repoLoad(self.dbobj.path)
        return repo

    def _pre_save(self):
        pass

    def __repr__(self):
        return self.dbobj.path

    __str__ = __repr__
