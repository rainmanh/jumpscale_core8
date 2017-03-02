from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()

from peewee import *
from playhouse.sqlite_ext import Model

# from playhouse.sqlcipher_ext import *
# db = Database(':memory:')


class IssueCollection(base):
    """
    This class represent a collection of Issues
    """

    def _init(self):
        # init the index
        db = j.tools.issuemanager.indexDB

        class Issue(Model):
            key = CharField(index=True, default="")
            gitHostRefs = CharField(index=True, default="")
            title = CharField(index=True, default="")
            creationTime = TimestampField(index=True, default=j.data.time.epoch)
            modTime = TimestampField(index=True, default=j.data.time.epoch)
            inGithub = BooleanField(index=True, default=False)
            labels = CharField(index=True, default="")
            assignees = CharField(index=True, default="")
            milestone = CharField(index=True, default="")
            priority = CharField(index=True, default="minor")
            type = CharField(index=True, default="unknown")
            state = CharField(index=True, default="new")
            content = TextField(index=False, default="")
            repo = TextField(index=True, default="")

            class Meta:
                database = j.tools.issuemanager.indexDB
                # order_by = ["id"]

        self.index = Issue

        if db.is_closed():
            db.connect()
        db.create_tables([Issue], True)

    def add2index(self, **args):
        """
        key = CharField(index=True, default="")
        gitHostRefs = CharField(index=True, default="")
        title = CharField(index=True, default="")
        creationTime = TimestampField(index=True, default=j.data.time.epoch)
        modTime = TimestampField(index=True, default=j.data.time.epoch)
        inGithub = BooleanField(index=True, default=False)
        labels = CharField(index=True, default="")
        assignees = CharField(index=True, default="")
        milestone = CharField(index=True, default="")
        priority = CharField(index=True, default="minor")
        type = CharField(index=True, default="unknown")
        state = CharField(index=True, default="new")
        content = TextField(index=False, default="")
        repo = TextField(index=True, default="")

        @param args is any of the above

        assignees & labels can be given as:
            can be "a,b,c"
            can be "'a','b','c'"
            can be ["a","b","c"]
            can be "a"

        """

        if "gitHostRefs" in args:
            args["gitHostRefs"] = ["%s_%s_%s" % (item["name"], item["id"], item['url']) for item in args["gitHostRefs"]]

        args = self._arraysFromArgsToString(["assignees", "labels", "gitHostRefs"], args)

        # this will try to find the right index obj, if not create
        obj, isnew = self.index.get_or_create(key=args["key"])

        for key, item in args.items():
            if key in obj._data:
                # print("%s:%s" % (key, item))
                obj._data[key] = item

        obj.save()

    def getFromGitHostID(self, git_host_name, git_host_id, git_host_url, createNew=True):
        return j.clients.gogs._getFromGitHostID(self, git_host_name=git_host_name, git_host_id=git_host_id, git_host_url=git_host_url, createNew=createNew)
