from JumpScale import j
from JumpScale.baselib.jobcontroller.models.RunModel import RunModel

import capnp
from JumpScale.baselib.jobcontroller import model_job_capnp as ModelCapnp
from JumpScale.data.capnp.ModelBase import ModelBaseCollection



class RunsCollection(ModelBaseCollection):
    """
    This class represent a collection of Runs
    It's used to list/find/create new Instance of Run Model object
    """

    def __init__(self):
        self.logger = j.logger.get('j.jobcontroller.run-collection')
        # connection to the key-value store index repository namespace
        category = "Run"
        self.namespace_prefix = 'runs'
        namespace = "%s:%s" % (self.namespace_prefix, category.lower())
        db = j.servers.kvs.getRedisStore(namespace, namespace, **j.atyourservice.config['redis'])
        super().__init__(ModelCapnp.Run, category=category, namespace=namespace, modelBaseClass=RunModel, db=db, indexDb=db)

    def new(self):
        model = RunModel(
            key='',
            new=True,
            collection=self)
        return model

    def get(self, key):
        return RunModel(
            key=key,
            new=False,
            collection=self)

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

    def find(self, state="", repo="", fromEpoch=0, toEpoch=9999999999999):
        res = []
        for key in self._list_keys(state, fromEpoch, toEpoch):
            if self.exists(key):
                if repo:
                    model = self.get(key)
                    if model.dbobj.repo != repo:
                        continue
                res.append(self.get(key))
        return res

    def delete(self, state="", repo="", fromEpoch=0, toEpoch=9999999999999):
        for key in self._list_keys(state, fromEpoch, toEpoch):
            if repo:
                model = self.get(key)

                if model.dbobj.repo != repo.model.key:
                    continue
                idx = str(model.dbobj.state) + ':' + str(model.dbobj.lastModDate)
                self._index.index_remove(keys=idx)
                self._db.delete(key=key)
                # for job in model.jobs .. job. remove job
                for step in model.dbobj.steps:
                    for job in step.jobs:
                        j.core.jobcontroller.db.jobs._db.delete(job.key)


    def destroy(self):
        self._db.destroy()
        self._index.destroy()
