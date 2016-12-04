
from JumpScale import j

from JumpScale.tools.issuemanager.models.IssueModel import IssueModel
from JumpScale.tools.issuemanager.models.IssueCollection import IssueCollection

import capnp
from JumpScale.tools.issuemanager import model_capnp as ModelCapnp


class IssueManager:

    """

    """

    def __init__(self):
        self.__jslocation__ = "j.tools.issuemanager"
        self.dbIssues = IssueCollection()

    def getCapnpSchema(self):
        return ModelCapnp.Issue

    def getIssueCollectionFromDB(self, kvs=None):
        """
        std keyvalue stor is redis used by core
        """
        schema = self.getCapnpSchema()
        if not kvs:
            kvs = j.servers.kvs.getRedisStore(name="gogs", namespace="gogs:issue", unixsocket="%s/redis.sock" % j.dirs.tmpDir)

        collection = j.data.capnp.getModelCollection(
            schema, namespace="gogs:issue", category="issues", modelBaseClass=IssueModel,
            modelBaseCollectionClass=IssueCollection, db=kvs, indexDb=kvs)
        return collection
