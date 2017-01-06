from JumpScale import j
from JumpScale.data.capnp.ModelBase import ModelBaseCollection
import capnp
from JumpScale.baselib.atyourservice81 import model_capnp as ModelCapnp
from JumpScale.baselib.atyourservice81.models.RepoModel import RepoModel


class ReposCollections(ModelBaseCollection):
    """
    This class represent a collection of AYS Reposities
    It's used to list/find/create new Instance of Repository Model object
    """
    #

    def __init__(self):
        db = j.servers.kvs.getARDBStore("ays:repo", "ays:repo", **j.atyourservice.config['redis'])
        super().__init__(schema=ModelCapnp.Repo, category="Repo", namespace="ays:repo", modelBaseClass=RepoModel, db=db, indexDb=db)

    def _list_keys(self, path="", returnIndex=False):
        """
        Return a list of all the keys contained in the KVS.
        """
        if path == "":
            path = ".*"
        regex = "^%s$" % (path)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, path=""):
        """
        Find look in the KVS for a Repositories with the path in argument and returns a list of Repository object
        matching the research
        """
        res = []
        for key in self._list_keys(path):
            res.append(self.get(key))
        return res

if __name__ == '__main__':
    repos = ReposCollections()
    from IPython import embed
    embed()
