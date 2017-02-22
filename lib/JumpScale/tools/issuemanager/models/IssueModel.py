
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class IssueModel(base):
    """
    Model Class for an Issue object
    """

    def index(self):

        i = self.collection.add2index(**self.to_dict())

        # a = self.collection.add2index(title="this is a title", assignees='kristof,jan ,pol,oo')
        # b = self.collection.add2index(title="this is a title", assignees=['kristof', 'jan'])
        # c = self.collection.add2index(title="this is a2 title", assignees='kristof')

        # self.collection._index.get_or_create(title="this is a title")

        # source = ""
        # gogsRefs = ",".join(["%s_%s" % (item.name.lower(), item.id) for item in self.dbobj.gogsRefs])
        # # for item in self.dbobj.gogsRefs:
        # # there can be multiple gogs sources
        # # self.collection._index.lookupSet("gogs_%s" % item.name, item.id, self.key)
        #
        # # put indexes in db as specified
        # if self.dbobj.isClosed:
        #     closed = 1
        # else:
        #     closed = 0
        #
        # assignees = ",".join([str(item) for item in self.dbobj.assignees])
        # labels = ",".join([str(item).replace(":", ";") for item in self.dbobj.labels])
        #
        # ind = "%s:%s:%s:%s:%s:%s:%s:%s:%s" % (self.dbobj.milestone, self.dbobj.creationTime,
        #                                       self.dbobj.modTime, closed, self.dbobj.repo, self.dbobj.title.lower().replace(":", ";"),
        #                                       assignees, labels, gogsRefs)
        # self.collection._index.index({ind: self.key})

    def _pre_save(self):
        # process the labels to our proper structure
        labels = [item for item in self.dbobj.labels]
        if labels != []:
            toremove = []
            for label in labels:
                if label.startswith("type_"):
                    toremove.append(label)
                    label = label[5:]
                    self.dbobj.type = label
                elif label.startswith("priority_"):
                    toremove.append(label)
                    label = label[9:]
                    self.dbobj.priority = label
                elif label.startswith("state_"):
                    toremove.append(label)
                    label = label[6:]
                    self.dbobj.state = label
            self.initSubItem("labels")
            for item in toremove:
                self.list_labels.pop(self.list_labels.index(item))
            self.reSerialize()

    def gogsRefSet(self, name, id):
        return j.clients.gogs._gogsRefSet(self, name, id)

    def gogsRefExist(self, name):
        return j.clients.gogs._gogsRefExist(self, name)

    def gogsRefGet(self, name):
        return j.clients.gogs._gogsRefGet(self, name)

    def assigneeSet(self, key):
        """
        @param key is the unique key of the member
        """
        if key not in self.dbobj.assignees:
            self.addSubItem("assignees", key)
        self.changed = True

    def commentSet(self, comment, owner=""):
        if owner == None:
            owner = ""
        for item in self.dbobj.comments:
            if item.comment != comment:
                item.comment == comment
                self.changed = True
            if item.owner != owner:
                item.owner == owner
                self.changed = True
            return
        obj = self.collection.list_comments_constructor(comment=comment, owner=owner)
        self.addSubItem("comments", obj)
        self.changed = True
