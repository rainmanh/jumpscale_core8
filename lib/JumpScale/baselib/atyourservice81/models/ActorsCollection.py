from JumpScale import j
from JumpScale.data.capnp.ModelBase import ModelBaseCollection
import capnp
from JumpScale.baselib.atyourservice81 import model_capnp as ModelCapnp
from JumpScale.baselib.atyourservice81.models.ActorModel import ActorModel


class ActorsCollection(ModelBaseCollection):
    """
    This class represent a collection of AYS Actors contained in an AYS repository
    It's used to list/find/create new Instance of Actor Model object
    """

    def __init__(self, repository):
        self.repository = repository
        namespace = "ays:%s:actor" % repository.name
        db = j.servers.kvs.getRedisStore(namespace, namespace, **j.atyourservice.config['redis'])
        super().__init__(
            schema=ModelCapnp.Actor,
            category="Actor",
            namespace=namespace,
            modelBaseClass=ActorModel,
            db=db,
            indexDb=db
        )

    def new(self):
        model = ActorModel(
            aysrepo=self.repository,
            capnp_schema=ModelCapnp.Actor,
            category=self.category,
            db=self._db,
            index=self._index,
            key='',
            new=True)
        return model

    def get(self, key):
        model = ActorModel(
            aysrepo=self.repository,
            capnp_schema=ModelCapnp.Actor,
            category=self.category,
            db=self._db,
            index=self._index,
            key=key,
            new=False)
        return model

    def _list_keys(self, name="", state="", returnIndex=False):
        """
        @param name can be the full name e.g. node.ssh or a rule but then use e.g. node.*  (are regexes, so need to use .* at end)
        @param state
            new
            ok
            error
            disabled
        """
        if name == "":
            name = ".*"
        if state == "":
            state = ".*"
        regex = "%s:%s" % (name, state)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, name="", state=""):
        """
        @param name can be the full name e.g. node.ssh or a rule but then use e.g. node.*  (are regexes, so need to use .* at end)
        @param state
            new
            ok
            error
            disabled
        """
        res = []
        for key in self._list_keys(name, state):
            res.append(self.get(key))
        return res
