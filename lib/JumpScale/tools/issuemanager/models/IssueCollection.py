from JumpScale import j
import capnp
from JumpScale.tools.issuemanager import model_capnp as ModelCapnp
from JumpScale.tools.issuemanager.models.IssueModel import IssueModel

base = j.data.capnp.getModelBaseClassCollection()


class IssuesCollection(base):
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


    def _list_keys(self, repoId='', title='', milestoneId='', assigneeId='', isClosed='',
                   numComments='', returnIndex=False):
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
        if repoId == "":
            repoId = ".*"
        if title == "":
            title = ".*"
        if milestoneId == "":
            milestoneId = ".*"
        if assigneeId == "":
            assigneeId = ".*"
        if isClosed == "":
            isClosed = ".*"
        if numComments == "":
            numComments = ".*"
        regex = "%s:%s:%s:%s:%s" % (repoId, title, milestoneId, assigneeId, isClosed)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, issueId='', repoId='', title='', content='', milestoneId='', assigneeId='', is_closed='',
             num_comments=''):

        res = []
        for key in self._list_keys(repoId, title, content, milestoneId, assigneeId, is_closed):
            res.append(self.get(key))
        return res
