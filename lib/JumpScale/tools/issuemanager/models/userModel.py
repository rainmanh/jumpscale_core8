
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class UserModel(base):
    """
    Model Class for an Issue object
    """


    def index(self):
        # put indexes in db as specified
        ind = "%s:%s:%s:%s:%s" % (self.dbobj.name.lower(), self.dbobj.fullname.lower(), self.dbobj.email,
                                  self.dbobj.id, self.dbobj.source.lower())
        self._index.index({ind: self.key})
        from IPython import embed
        print ("DEBUG NOW UserModel index")
        embed()
        raise RuntimeError("stop debug here")

    def _pre_save(self):
        pass
