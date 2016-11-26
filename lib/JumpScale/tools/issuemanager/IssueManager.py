
from JumpScale import j

from JumpScale.tools.issuemanager.models.IssueCollection import IssueCollection

class IssueManager:

    """

    """

    def __init__(self):
        self.__jslocation__ = "j.tools.issuemanager"
        self.dbIssues=IssueCollection()
