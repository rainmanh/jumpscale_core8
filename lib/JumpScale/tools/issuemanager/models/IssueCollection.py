from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class IssuesCollection(base):
    """
    This class represent a collection of AYS Issues contained in an AYS repository
    It's used to list/find/create new Instance of Issue Model object
    """

    def find(self, name="", state=""):
        """
        @param state
            new
            ok
            error
            disabled
        """
        #@TODO: *1 needs to be properly implemented
        res = []
        for key in self._list_keys(name, state):
            res.append(self.get(key))
        return res
