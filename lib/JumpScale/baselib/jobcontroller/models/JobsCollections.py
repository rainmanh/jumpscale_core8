from JumpScale import j
from JumpScale.baselib.jobcontroller.models.JobModel import JobModel

import capnp
from JumpScale.baselib.jobcontroller import model_job_capnp as ModelCapnp



class JobsCollection:
    """
    This class represent a collection of Jobs
    It's used to list/find/create new Instance of Job Model object
    """

    def __init__(self):
        # connection to the key-value store index repository namespace
        self.category = "Job"
        self.namespace_prefix = 'jobs'
        namespace = "%s:%s" % (self.namespace_prefix, self.category.lower())
        self._db = j.servers.kvs.getRedisStore(namespace, namespace, **j.atyourservice.config['redis'])
        # for now we do index same as database
        self._index = j.servers.kvs.getRedisStore(namespace, namespace, **j.atyourservice.config['redis'])

    def new(self):
        model = JobModel(
            capnp_schema=ModelCapnp.Job,
            category=self.category,
            db=self._db,
            index=self._index,
            key='',
            new=True)
        return model

    def get(self, key):
        return JobModel(
            capnp_schema=ModelCapnp.Job,
            category=self.category,
            db=self._db,
            index=self._index,
            key=key,
            new=False)

    def exists(self, key):
        return self._db.exists(key)

    def _list_keys(self, actor="", service="", action="", state="", serviceKey="", fromEpoch=0, toEpoch=9999999999999, returnIndex=False):
        if actor == "":
            actor = ".*"
        if service == "":
            service = ".*"
        if action == "":
            action = ".*"
        if state == "":
            state = ".*"
        if serviceKey == "":
            serviceKey = ".*"
        epoch = ".*"
        regex = "%s:%s:%s:%s:%s:%s" % (actor, service, action, state, serviceKey, epoch)
        res0 = self._index.list(regex, returnIndex=True)
        res1 = []
        for index, key in res0:
            epoch = int(index.split(":")[-1])
            if fromEpoch < epoch and epoch < toEpoch:
                if returnIndex:
                    res1.append((index, key))
                else:
                    res1.append(key)
        return res1

    def find(self, actor="", service="", action="", state="", serviceKey="", fromEpoch=0, toEpoch=9999999999999):
        res = []
        for key in self._list_keys(actor, service, action, state, serviceKey, fromEpoch, toEpoch):
            res.append(self.get(key))
        return res

    def destroy(self):
        self._db.destroy()
        self._index.destroy()
