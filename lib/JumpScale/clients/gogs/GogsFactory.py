from GogsClient import GogsClient
from JumpScale import j


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

        issueCollection = j.tools.issuemanager.getIssueCollectionFromDB()

        model = j.clients.peewee.getModel(ipaddr=ipaddr, port=port, login=login, passwd=passwd, dbname=dbname)

        # TODO: *1 need to be only 1 query

        for issue in model.Issue.select():
            # setting issue info
            issue_model = issueCollection.new()
            issue_model.dbobj.title = issue.name
            issue_model.dbobj.content = issue.content
            issue_model.dbobj.isClosed = issue.is_closed
            issue_model.dbobj.nrComments = issue.num_comments
            issue_model.dbobj.id = issue.id

            try:
                # label info
                label_id = model.IssueLabel.get(model.IssueLabel.issue == issue.id).label
                label = model.Label.get(model.Label.id == label_id)

                issue_model.dbobj.label.name = label.name
                issue_model.dbobj.label.color = label.color
            except model.IssueLabel.DoesNotExist:
                pass

            try:
                # milestone info
                milestone = model.Milestone.get(model.Milestone.id == issue.milestone)
                issue_model.dbobj.milestone.name = milestone.name
                issue_model.dbobj.milestone.isClosed = milestone.is_closed
                issue_model.dbobj.milestone.numIssues = milestone.num_issues
                issue_model.dbobj.milestone.numClosed = milestone.num_closed_issues
                issue_model.dbobj.milestone.completeness = milestone.completeness
                issue_model.dbobj.milestone.deadline = milestone.deadline_unix
            except model.Milestone.DoesNotExist:
                pass

            try:
                # assignee info
                user = model.User.get(model.User.id == issue.assignee)
                issue_model.dbobj.assignee.name = user.name
                issue_model.dbobj.assignee.fullname = user.full_name
                issue_model.dbobj.assignee.email = user.email
            except model.User.DoesNotExist:
                pass

            try:
                # repository info
                repo = model.Repository.get(model.Repository.id == issue.repo)
                issue_model.dbobj.repo.name = repo.name
                issue_model.dbobj.repo.description = repo.description
                issue_model.dbobj.repo.numIssues = repo.num_issues
                issue_model.dbobj.repo.numMilestones = repo.num_milestones
                # repository owner info
                owner = model.User.get(model.User.id == repo.owner)
                issue_model.dbobj.repo.owner.name = owner.name
                issue_model.dbobj.repo.owner.fullname = owner.full_name
                issue_model.dbobj.repo.owner.email = owner.email
            except model.Repository.DoesNotExist:
                pass

            issue_model.save()
