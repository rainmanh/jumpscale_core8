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
            gogsRefs = CharField(index=True, default="")
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

            class Meta:
                database = j.tools.issuemanager.indexDB
                # order_by = ["id"]

        # class Assignee(Model):
        #     issue = ForeignKeyField(Issue, related_name='assignees')
        #     name = CharField(index=True)

        self.index = Issue

        db.connect()
        db.create_tables([Issue], True)

    def add2index(self, **args):
        """
        key = CharField(index=True, default="")
        gogsRefs = CharField(index=True, default="")
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

        @param args is any of the above

        assignees & labels can be given as:
            can be "a,b,c"
            can be "'a','b','c'"
            can be ["a","b","c"]
            can be "a"

        """

        if "gogsRefs" in args:
            args["gogsRefs"] = ["%s_%s" % (item["name"], item["id"]) for item in args["gogsRefs"]]

        args = self._toArray(["assignees", "labels", "gogsRefs"], args)

        # this will try to find the right index obj, if not create
        obj, isnew = self.index.get_or_create(key=args["key"])

        for key, item in args.items():
            if key in obj._data:
                # print("%s:%s" % (key, item))
                obj._data[key] = item

        obj.save()

    def list(self,  query=None, repos=[], title='', content="", isClosed=None, comment='.*',
             assignees=[], milestones=[], labels=[], gogsId="", gogsName="", github=False,
             fromTime=None, toTime=None, fromCreationTime=None, toCreationTime=None, returnIndex=False):
        """
        List all keys of issue model with specified params.

        @param repo int,, id of repo the issue belongs to.
        @param title str,, title of issue.
        @param milestone int,, milestone id set to this issue.
        @param isClosed bool,, issue is closed.

        @param if query not none then will use the index to do a query and ignore other elements

        e.g
          -  self.index.select().order_by(self.index.modTime.desc())
          -  self.index.select().where((self.index.priority=="normal") | (self.index.priority=="critical"))

         info how to use see:
            http://docs.peewee-orm.com/en/latest/peewee/querying.html
            the query is the statement in the where

        """

        #[item._data for item in self.index.select().where((self.index.priority=="normal"))]

        # TODO: use query functionality in peewee to implement above

        if query != None:
            res = [item.key for item in query]
        else:
            res = [item.key for item in self.index.select().order_by(self.index.modTime.desc())]
            # raise NotImplemented()

        return res

    def find(self, query=None, repos=[], title='', content="", isClosed=None, comment='.*',
             assignees=[], milestones=[], labels=[], gogsName="", gogsId="", github=False,
             fromTime=None, toTime=None, fromCreationTime=None, toCreationTime=None):
        """
        """
        res = []
        for key in self.list(query=query, repos=repos, title=title, content=content, isClosed=isClosed, comment=comment, assignees=assignees, milestones=milestones,
                             labels=labels, gogsName=gogsName, gogsId=gogsId, github=github, fromTime=fromTime,
                             toTime=toTime, fromCreationTime=fromCreationTime, toCreationTime=toCreationTime):
            res.append(self.get(key))

        return res

    def getFromGogsId(self, gogsName, gogsId, createNew=True):
        return j.clients.gogs._getFromGogsId(self, gogsName=gogsName, gogsId=gogsId, createNew=createNew)
