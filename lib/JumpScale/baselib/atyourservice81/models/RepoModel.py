from JumpScale import j
from JumpScale.data.capnp.ModelBase import ModelBase


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

    def index(self):
        # put indexes in db as specified
        ind = "%s" % (self.dbobj.path)
        self._index.index({ind: self.key})

    def delete(self):
        self._db.delete(self.key)
        self._index.index_remove(self.path)

    def objectGet(self):
        """
        returns an Actor object created from this model
        """
        try:
            repo = j.atyourservice._repoLoad(self.dbobj.path)
        except j.exceptions.NotFound as err:
            self.logger.error(
                "Repository at {path} doesn't exists. remove it from database".format(path=self.dbobj.path))
            self.delete()
            raise err

        return repo

    def _pre_save(self):
        pass

    def __repr__(self):
        return self.dbobj.path

    __str__ = __repr__
