from GogsClient import GogsClient
from JumpScale import j
from JumpScale.tools.issuemanager.models.IssueCollection import IssuesCollection


class GogsFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.gogs"
        self.logger = j.logger.get("j.clients.gogs")
        # self.db = ModelsFactory()

    def getRestClient(self, addr='https://127.0.0.1', port=3000, login='root', passwd='root'):
        return GogsClient(addr=addr, port=port, login=login, passwd=passwd)

    def getDataFromPSQL(self, ipaddr="127.0.0.1", port=5432, login="gogs", passwd="something", dbname="gogs"):
        """
        get peewee model from psql database from gogs & then load in our capnp database
        """
        model = j.clients.peewee.getModel(ipaddr=ipaddr, port=port, login=login, passwd=passwd, dbname=dbname)
        for issue in model.Issue.select():
            issues_obj = IssuesCollection()
            issue_model = issues_obj.new()
            issue_model.dbobj.title = issue.name
            issue_model.dbobj.content = issue.content
            issue_model.dbobj.isClosed = issue.is_closed
            issue_model.dbobj.milestoneId = issue.milestone
            issue_model.dbobj.numComments = issue.num_comments
            issue_model.dbobj.repoId = issue.repo

            #getting from differnet database
            issue_model.dbobj.labelId = model.IssueLabel.get(model.IssueLabel.issue == issue.id).label
            issue_model.save()