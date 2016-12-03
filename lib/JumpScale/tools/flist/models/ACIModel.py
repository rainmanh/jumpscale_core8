
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class ACIModel(base):
    """
    class for ACL item = Access Control Item
    """

    @property
    def key(self):
        if self._key == "":
            from IPython import embed
            print("DEBUG NOW generate key")
            embed()
            raise RuntimeError("stop debug here acimodel")
        return self._key
