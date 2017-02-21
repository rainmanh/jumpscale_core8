from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class IssueCollection(base):
    """
    This class represent a collection of Issues
    """

    def list(self,  repos=[], title='', content="", isClosed=None, comment='.*',
             assignees=[], milestones=[], labels=[], gogsName="", gogsId="", github=False,
             fromTime=None, toTime=None, fromCreationTime=None, toCreationTime=None, returnIndex=False):
        """
        List all keys of issue model with specified params.

        @param repo int,, id of repo the issue belongs to.
        @param title str,, title of issue.
        @param milestone int,, milestone id set to this issue.
        @param isClosed bool,, issue is closed.
        @param id int,, issue id in db.
        @param creationTime int,, epoch of creation of issue.
        @param modTime int,, epoch of modification of issue.
        @param source str,, s
        ource of remote database.
        @param returnIndexalse bool,, return the index used.
        """

        # TODO: *1 needs to be seriously checked

        # ind = "%d:%d:%d:%d:%d:%d:%s:%s:%s" % (self.dbobj.milestone, self.dbobj.creationTime,
        # self.dbobj.modTime, closed, self.dbobj.repo, self.dbobj.title.lower(),
        # assignees, labels, gogsRefs)

        if title == "":
            title0 = ".*"

        if isClosed is None:
            isClosed0 = ".*"
        elif isClosed is True:
            isClosed = '1'
        elif isClosed is False:
            isClosed = '0'

        regex = ".*:.*:.*:%s:.*:%s:.*:.*:.*" % (isClosed0, title0,)
        keys = self._index.list(regex, returnIndex=True)
        res = []
        for indexItem, key in keys:
            # print(indexItem)
            milestone1, creationTime1, modTime1, closed1, repo1, title1, assignees1, labels1, gogsrefs1 = indexItem.split(
                ":")
            modTime1 = int(modTime1)
            creationTime1 = int(creationTime1)
            if closed1 == "1":
                closed1 = True
            else:
                closed1 = False
            gogsName1, gogsId1 = gogsrefs1.split("_")

            if gogsName != "" and gogsName1 != gogsName:
                continue

            if gogsId != "" and gogsId1 != gogsId:
                continue

            if fromTime != None and fromTime > modTime1 - 1:
                continue

            if toTime != None and modTime1 + 1 > toTime:
                continue

            if fromCreationTime != None and fromCreationTime > creationTime1 - 1:
                continue

            if toCreationTime != None and creationTime1 + 1 > toCreationTime:
                continue

            if isClosed != None and isClosed != closed1:
                continue

            # milestone
            if milestones != []:
                found = False
                for milestone in milestones:
                    if milestone == milestone1:
                        found = True
                if found == False:
                    continue

            # labels
            if labels != []:
                found = False
                for label in labels:
                    if label == label1:
                        found = True
                if found == False:
                    continue

            # did not continue so now only to check description & content
            if content != '' or title != '':
                obj = self.get(key)
                if content != "" and obj.dbobj.content != content:
                    continue
                if title != "" and obj.dbobj.title != title:
                    continue

            res.append(key)

        return res

    def find(self, repos=[], title='', content="", isClosed=None, comment='.*',
             assignees=[], milestones=[], labels=[], gogsName="", gogsId="", github=False,
             fromTime=None, toTime=None, fromCreationTime=None, toCreationTime=None):
        """
        """
        res = []
        for key in self.list(repos=repos, title=title, content=content, isClosed=isClosed, comment=comment, assignees=assignees, milestones=milestones,
                             labels=labels, gogsName=gogsName, gogsId=gogsId, github=github, fromTime=fromTime,
                             toTime=toTime, fromCreationTime=fromCreationTime, toCreationTime=toCreationTime):
            res.append(self.get(key))

        return res

    def getFromGogsId(self, gogsName, gogsId, createNew=True):
        return j.clients.gogs._getFromGogsId(self, gogsName=gogsName, gogsId=gogsId, createNew=createNew)
