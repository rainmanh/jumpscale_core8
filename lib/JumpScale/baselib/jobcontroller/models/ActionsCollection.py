from JumpScale import j
from JumpScale.baselib.jobcontroller.models.ActionModel import ActionModel

import capnp
from JumpScale.baselib.jobcontroller import model_job_capnp as ModelCapnp


class ActionsCollection:
    """
    This class represent a collection of AYS Reposities
    It's used to list/find/create new Instance of Repository Model object
    """

    def __init__(self):
        # connection to the key-value store index repository namespace
        self.category = "Action"
        self.namespace_prefix = 'jobs'
        namespace = "%s:%s" % (self.namespace_prefix, self.category.lower())
        self._db = j.servers.kvs.getRedisStore(namespace, namespace, **j.atyourservice.config['redis'])
        # for now we do index same as database
        self._index = j.servers.kvs.getRedisStore(namespace, namespace, **j.atyourservice.config['redis'])

    def new(self):
        model = ActionModel(
            capnp_schema=ModelCapnp.Action,
            category=self.category,
            db=self._db,
            index=self._index,
            key='',
            new=True)
        return model

    def get(self, key):
        return ActionModel(
            capnp_schema=ModelCapnp.Action,
            category=self.category,
            db=self._db,
            index=self._index,
            key=key,
            new=False)

    def exists(self, key):
        return self._db.exists(key)

    def _list_keys(self, origin="", name="", returnIndex=False):
        if name == "":
            name = ".*"
        if origin == "":
            origin = ".*"
        regex = "%s:%s" % (origin, name)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, origin="", name=""):
        res = []
        for key in self._list_keys(origin, name):
            res.append(self.get(key))
        return res

    def destroy(self):
        self._db.destroy()
        self._index.destroy()