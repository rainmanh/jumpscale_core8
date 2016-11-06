from JumpScale import j
from JumpScale.baselib.atyourservice81.models.ActorModel import ActorModel

import capnp
from JumpScale.baselib.atyourservice81 import model_capnp as ModelCapnp


class ActorsCollection:
    """
    This class represent a collection of AYS Actors contained in an AYS repository
    It's used to list/find/create new Instance of Actor Model object
    """

    def __init__(self, repository, host=None, port=None, unixsocket=None):
        self.repository = repository
        self.category = "Actor"
        self.namespace_prefix = 'ays:{}'.format(repository.name)
        namespace = "%s:%s" % (self.namespace_prefix, self.category.lower())
        self.repository = repository
        self._db = j.servers.kvs.getRedisStore(namespace, namespace, **j.atyourservice.config['redis'])
        # for now we do index same as database
        self._index = j.servers.kvs.getRedisStore(namespace, namespace, **j.atyourservice.config['redis'])

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

    def destroy(self):
        self._db.destroy()
        self._index.destroy()
