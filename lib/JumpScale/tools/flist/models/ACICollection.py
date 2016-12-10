from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class ACICollection(base):
    """
    """

    def list(self, id=0):
        """
        """
        if id == 0:
            name = ".*"
        else:
            regex = "%s" % (id)
        res = self._index.list(regex, returnIndex=True)
        return res

    def find(self, id=0):
        """
        """
        res = []
        for key in self.list(id=id):
            res.append(self.get(key))
        return res

    def lookup(self, id):
        return self._index.lookupGet("id", id)
