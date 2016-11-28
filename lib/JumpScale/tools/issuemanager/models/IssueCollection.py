from JumpScale import j
from JumpScale.tools.issuemanager.models.IssueModel import IssueModel

import capnp
from JumpScale.tools.issuemanager import model as ModelCapnp


class IssueCollection:
    """
    This class represent a collection of Issues
    It's used to list/find/create new Instance of Issue Model object
    """

    def __init__(self):
        self.repository = repository
        self.category = "Issue"
        namespace=self.category
        self.capnp_schema = ModelCapnp.Issue
        self.repository = repository
        self._db = j.servers.kvs.getRedisStore(name=namespace, namespace=namespace)
        # for now we do index same as database
        self._index = j.servers.kvs.getRedisStore(namespace, namespace)

    def new(self):
        model = IssueModel(
            capnp_schema=ModelCapnp.Issue,
            category=self.category,
            db=self._db,
            index=self._index,
            key='',
            new=True)
        return model

    def get(self, key):
        model = IssueModel(
            aysrepo=self.repository,
            capnp_schema=ModelCapnp.Issue,
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
