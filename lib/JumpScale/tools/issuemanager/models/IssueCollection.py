from JumpScale import j
import capnp
from JumpScale.tools.issuemanager import model_capnp as ModelCapnp
from JumpScale.tools.issuemanager.models.IssueModel import IssueModel

base = j.data.capnp.getModelBaseClassCollection()


class IssueCollection(base):
    """
    This class represent a collection of AYS Issues contained in an AYS repository
    It's used to list/find/create new Instance of Issue Model object
    """
    def __init__(self):
        namespace = "gogs:issue"
        db = j.servers.kvs.getRedisStore(namespace, namespace, unixsocket='/tmp/redis.sock')
        super().__init__(
            schema=ModelCapnp.Issue,
            category="Issue",
            namespace=namespace,
            modelBaseClass=IssueModel,
            db=db,
            indexDb=db
        )


    def _list_keys(self, repo='', title='', milestone='', assignee='', isClosed='', numComments='', returnIndex=False):
        """
        @param name can be the full name e.g. myappserver or a prefix but then use e.g. myapp.*
        @param actor can be the full name e.g. node.ssh or role e.g. node.* (but then need to use the .* extension, which will match roles)
        @param parent is in form $actorName!$instance
        @param producer is in form $actorName!$instance

        @param state:
            new
            installing
            ok
            error
            disabled
            changed

        """
        if repo == "":
            repo = ".*"
        if title == "":
            title = ".*"
        if milestone == "":
            milestone = ".*"
        if assignee == "":
            assignee = ".*"
        if isClosed == "":
            isClosed = ".*"
        if numComments == "":
            numComments = ".*"
        regex = "%s:%s:%s:%s:%s" % (repo, title, milestone, assignee, isClosed)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, issueId='', repo='', title='', milestone='', assignee='', is_closed='', num_comments=''):

        res = []
        for key in self._list_keys(repo, title, milestone, assignee, is_closed):
            res.append(self.get(key))
        return res
