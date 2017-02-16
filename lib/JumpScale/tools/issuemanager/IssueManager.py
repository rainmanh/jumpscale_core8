
from JumpScale import j

from JumpScale.tools.issuemanager.models.IssueModel import IssueModel
from JumpScale.tools.issuemanager.models.IssueCollection import IssueCollection
from JumpScale.tools.issuemanager.models.userModel import UserModel
from JumpScale.tools.issuemanager.models.userCollection import UserCollection
from JumpScale.tools.issuemanager.models.repoModel import RepoModel
from JumpScale.tools.issuemanager.models.repoCollection import RepoCollection
from JumpScale.tools.issuemanager.models.orgModel import OrgModel
from JumpScale.tools.issuemanager.models.orgCollection import OrgCollection
import capnp
from JumpScale.tools.issuemanager import model_capnp as ModelCapnp


class IssueManager:

    """

    """

    def __init__(self):
        self.__jslocation__ = "j.tools.issuemanager"

    def getIssueSchema(self):
        """
        Return capnp schema for issues struct
        """
        return ModelCapnp.Issue

    def getUserSchema(self):
        """
        Return capnp schema for user struct
        """
        return ModelCapnp.User

    def getRepoSchema(self):
        """
        Return capnp schema for repo struct
        """
        return ModelCapnp.Repo

    def getOrgSchema(self):
        """
        Return capnp schema for org struct
        """
        return ModelCapnp.Organization

    def getIssueCollectionFromDB(self, kvs=None):
        """
        std keyvalue stor is redis used by core
        """
        schema = self.getIssueSchema()
        if not kvs:
            kvs = j.servers.kvs.getRedisStore(name="gogs", namespace="gogs:issue",
                                              unixsocket="/tmp/redis.sock")

        collection = j.data.capnp.getModelCollection(
            schema, namespace="gogs:issue", category="issues", modelBaseClass=IssueModel,
            modelBaseCollectionClass=IssueCollection, db=kvs, indexDb=kvs)
        return collection

    def getUserCollectionFromDB(self, kvs=None):
        schema = self.getUserSchema()
        if not kvs:
            kvs = j.servers.kvs.getRedisStore(name="gogs", namespace="gogs:user",
                                              unixsocket="/tmp/redis.sock")

        collection = j.data.capnp.getModelCollection(
            schema, namespace="gogs:user", category="user", modelBaseClass=UserModel,
            modelBaseCollectionClass=UserCollection, db=kvs, indexDb=kvs)
        return collection

    def getRepoCollectionFromDB(self, kvs=None):
        schema = self.getRepoSchema()
        if not kvs:
            kvs = j.servers.kvs.getRedisStore(name="gogs", namespace="gogs:repo",
                                              unixsocket="/tmp/redis.sock")

        collection = j.data.capnp.getModelCollection(
            schema, namespace="gogs:repo", category="repo", modelBaseClass=RepoModel,
            modelBaseCollectionClass=RepoCollection, db=kvs, indexDb=kvs)
        return collection

    def getOrgCollectionFromDB(self, kvs=None):
        schema = self.getOrgSchema()
        if not kvs:
            kvs = j.servers.kvs.getRedisStore(name="gogs", namespace="gogs:org",
                                              unixsocket="/tmp/redis.sock")

        collection = j.data.capnp.getModelCollection(
            schema, namespace="gogs:org", category="orgs", modelBaseClass=OrgModel,
            modelBaseCollectionClass=OrgCollection, db=kvs, indexDb=kvs)
        return collection
