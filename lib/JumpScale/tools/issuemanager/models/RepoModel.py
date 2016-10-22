from JumpScale import j

ModelBase = j.data.capnp.getModelBaseClass()

# from collections import OrderedDict


class RepoModel(ModelBase):
    """
    """

    @classmethod
    def list(self, actor="", service="", action="", state="", serviceKey="", fromEpoch=0, toEpoch=9999999999999, returnIndex=False):
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

    def index(self):
        # put indexes in db as specified
        ind = "%s:%s:%s:%s:%s:%s" % (self.dbobj.actorName, self.dbobj.serviceName,
                                     self.dbobj.actionName, self.dbobj.state, self.dbobj.serviceKey, self.dbobj.lastModDate)
        self._index.index({ind: self.key})

    @classmethod
    def find(self, actor="", service="", action="", state="", serviceKey="", fromEpoch=0, toEpoch=9999999999999):
        res = []
        for key in self.list(actor, service, action, state, serviceKey, fromEpoch, toEpoch):
            res.append(self._modelfactory.get(key))
        return res

    # @property
    # def dictFiltered(self):
    #     ddict = self.dbobj.to_dict()
    #     to_filter = ['args', 'result', 'profileData']
    #     for key in to_filter:
    #         if key in ddict:
    #             del ddict[key]
    #     return ddict

    # def __repr__(self):
    #     out = self.dictJson + "\n"
    #     if self.dbobj.args not in ["", b""]:
    #         out += "args:\n"
    #         out += self.argsJons
    #     return out
    #
    # __str__ = __repr__
