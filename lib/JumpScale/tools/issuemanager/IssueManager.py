
from JumpScale import j

from JumpScale.clients.gogs.models import IssueModel
from JumpScale.clients.gogs.models import IssueCollection

import capnp
from JumpScale.tools.issuemanager import model_capnp as ModelCapnp


class IssueManager:

    """

    """

    def __init__(self):
        self.__jslocation__ = "j.tools.issuemanager"
        self.dbIssues = IssueCollection()

    def getCapnpSchema(self):
        return ModelCapnp

    def getIssueCollectionFromDB(self, kvs=None):
        """
        std keyvalue stor is redis used by core
        """
        schema = self.getCapnpSchema()
        if kvs == None:
            kvs = j.servers.kvs.getRedisStore(name="test", unixsocket="%s/redis.sock" % j.dirs.tmpDir)

        collection = j.data.capnp.getModelCollection(
            schema, category="issues", modelBaseClass=IssueModel.IssueModel,
            modelBaseCollectionClass=IssueCollection.IssueCollection, db=kvs, indexDb=kvs)
        return collection
