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
        import ipdb; ipdb.set_trace()
        for issue in model.Issue.select():
            # get objects representing tables in the gogs db 
            user = model.User.get(model.User.id == issue.repo)
            milestone = model.Milestone.get(model.Milestone.id == issue.milestone)
            repo = model.Repository.get(model.Repository.id == issue.repo)

            label_id = model.IssueLabel.get(model.IssueLabel.issue == issue.id).label
            label = model.Label.get(model.Label.id == label_id)

            # setting issue info
            issues_obj = IssuesCollection()
            issue_model = issues_obj.new()
            issue_model.dbobj.title = issue.name
            issue_model.dbobj.content = issue.content
            issue_model.dbobj.isClosed = issue.is_closed
            issue_model.dbobj.numComments = issue.num_comments

            # milestone info
            issue_model.dbobj.milestone.name = milestone.name
            issue_model.dbobj.milestone.isClosed = milestone.is_closed
            issue_model.dbobj.milestone.numIssues = milestone.num_issues
            issue_model.dbobj.milestone.numClosed = milestone.num_closed_issues
            issue_model.dbobj.milestone.completeness = milestone.completeness
            issue_model.dbobj.milestone.deadline = milestone.deadline_unix

            # assignee info
            issue_model.dbobj.assignee.name = user.name
            issue_model.dbobj.assignee.fullname = user.full_name
            issue_model.dbobj.assignee.email = user.email

            # repository info
            issue_model.dbobj.repo.name = repo.name
            issue_model.dbobj.repo.description = repo.description
            issue_model.dbobj.repo.numIssues = repo.num_issues
            issue_model.dbobj.repo.numMilestones = repo.num_milestones
            # repository owner info
            owner = model.User.get(model.User.id == repo.owner)
            issue_model.dbobj.repo.owner.name = owner.name
            issue_model.dbobj.repo.owner.fullname = owner.full_name
            issue_model.dbobj.repo.owner.email = owner.email

            # label info
            issue_model.dbobj.label.name = label.name
            issue_model.dbobj.label.color = label.color

            issue_model.save()