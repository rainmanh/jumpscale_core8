from JumpScale import j
from JumpScale.baselib.jobcontroller.models.RunModel import RunModel

import capnp
from JumpScale.baselib.jobcontroller import model_job_capnp as ModelCapnp



class RunsCollection:
    """
    This class represent a collection of Runs
    It's used to list/find/create new Instance of Run Model object
    """

    def __init__(self):
        # connection to the key-value store index repository namespace
        self.category = "Job"
        self.namespace_prefix = 'runs'
        namespace = "%s:%s" % (self.namespace_prefix, self.category.lower())
        self._db = j.servers.kvs.getRedisStore(namespace, namespace, **j.atyourservice.config['redis'])
        # for now we do index same as database
        self._index = j.servers.kvs.getRedisStore(namespace, namespace, **j.atyourservice.config['redis'])

    def new(self):
        model = RunModel(
            capnp_schema=ModelCapnp.Run,
            category=self.category,
            db=self._db,
            index=self._index,
            key='',
            new=True)
        return model

    def get(self, key):
        return RunModel(
            capnp_schema=ModelCapnp.Run,
            category=self.category,
            db=self._db,
            index=self._index,
            key=key,
            new=False)

    def exists(self, key):
        return self._db.exists(key)

    def _list_keys(self, state="", fromEpoch=0, toEpoch=9999999999999, returnIndex=False):
        if state == "":
            state = ".*"
        epoch = ".*"
        regex = "%s:%s" % (state, epoch)
        res0 = self._index.list(regex, returnIndex=True)
        res1 = []
        for index, key in res0:
            epoch = int(index.split(":")[-1])
            if fromEpoch < epoch < toEpoch:
                if returnIndex:
                    res1.append((index, key))
                else:
                    res1.append(key)
        return res1

    def find(self, state="", fromEpoch=0, toEpoch=9999999999999):
        res = []
        for key in self._list_keys(state, fromEpoch, toEpoch):
            res.append(self.get(key))
        return res
    def destroy(self):
        self._db.destroy()
        self._index.destroy()
