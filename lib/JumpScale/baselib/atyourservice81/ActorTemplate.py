

from JumpScale import j

from collections import OrderedDict

# don't work with properties, this only happens when init is asked for so no big deal for performance


class ActorTemplate():

    def __init__(self, gitrepo, path, aysrepo=None):

        # path is path in gitrepo or absolute path

        self._schemaHrd = None

        if j.sal.fs.exists(path=path):
            # we know its absolute
            relpath = j.sal.fs.pathRemoveDirPart(
                path, gitrepo.baseDir, removeTrailingSlash=True)
            # path is now relative path
        else:
            relpath = path
            path = j.sal.fs.joinPaths(gitrepo.baseDir, path)
            if not j.sal.fs.exists(path=path):
                raise j.exceptions.Input(
                    "Cannot find path for template:%s" % path)

        self.path = path
        self.pathRelative = relpath

        base = j.sal.fs.getBaseName(relpath)
        self.name = base

        if aysrepo is None:
            # means the template comes from an ays repo
            self.domain = j.sal.fs.getBaseName(gitrepo.baseDir)
            if not self.domain.startswith("ays_"):
                raise j.exceptions.Input(
                    "name of ays template git repo should start with ays_, now:%s" % gitrepo.baseDir)
            self.domain = self.domain[4:]
        else:
            self.domain = j.sal.fs.getDirName(aysrepo.path, True)

        self.aysrepo = aysrepo

    @property
    def schemaHrd(self):
        """
        returns capnp schema as text
        """
        if self._schemaHrd is None:
            hrdpath = j.sal.fs.joinPaths(self.path, "schema.hrd")
            if j.sal.fs.exists(hrdpath):
                self._schemaHrd = j.data.hrd.getSchema(hrdpath)
            else:
                self._schemaHrd = ""
        return self._schemaHrd

    @property
    def schemaCapnpText(self):
        """
        returns capnp schema as text
        """
        path = j.sal.fs.joinPaths(self.path, "schema.capnp")
        if j.sal.fs.exists(path):
            return j.sal.fs.fileGetContents(path)
        if self.schemaHrd.capnpSchema is not "":
            return self.schemaHrd.capnpSchema
        return ""

    @property
    def _hrd(self):
        hrdpath = j.sal.fs.joinPaths(self.path, "actor.hrd")
        if j.sal.fs.exists(hrdpath):
            return j.data.hrd.get(hrdpath, prefixWithName=False)
        else:
            # check if we can find it in other ays template
            if self.name.find(".") != -1:
                name0 = self.name.split(".", 1)[0]
                templ = j.atyourservice.actorTemplateGet(name=name0, die=False)
                if templ is not None:
                    return templ.hrd
            return j.data.hrd.get(content="")

    @property
    def parentActor(self):
        parent = self.schemaHrd.parentSchemaItemGet()
        if parent is not None:
            parentrole = parent.parent

            res = self.aysrepo.db.actor.find(name="%s.*" % parentrole)
            if res == []:
                raise j.exceptions.Input(message="could not find parent:%s for %s" % (
                    parentrole, self), level=1, source="", tags="", msgpub="")
            elif len(res) > 1:
                raise j.exceptions.Input(message="found more than 1 parent:%s for %s" % (
                    parentrole, self), level=1, source="", tags="", msgpub="")
            parentobj = res[0].objectGet(self.aysrepo)
            return parentobj
        return None

    @property
    def producers(self):
        if self.schemaHrd.consumeSchemaItemsGet() != []:
            from IPython import embed
            print("DEBUG NOW producers")
            embed()
            raise RuntimeError("stop debug here")
            parent = self.schemaHrd.parentSchemaItemGet()
            if parent is not None:
                parentrole = parent.parent

                res = self.aysrepo.db.actor.find(name="%s.*" % parentrole)
                if res == []:
                    raise j.exceptions.Input(message="could not find parent:%s for %s" % (
                        parentrole, self), level=1, source="", tags="", msgpub="")
                elif len(res) > 1:
                    raise j.exceptions.Input(message="found more than 1 parent:%s for %s" % (
                        parentrole, self), level=1, source="", tags="", msgpub="")
                parentobj = res[0].objectGet(self.aysrepo)
                return parentobj
            return None
        return []

    @property
    def configDict(self):
        path = j.sal.fs.joinPaths(self.path, "actor.json")
        if j.sal.fs.exists(path, followlinks=True):
            ddict = j.data.serializer.json.load(path)
        else:
            ddict = {}
        ddict.update(self._hrd.getHRDAsDict())
        return ddict

    @property
    def configJSON(self):
        ddict2 = OrderedDict(self.configDict)
        return j.data.serializer.json.dumps(ddict2, sort_keys=True, indent=True)

    @property
    def dataUI(self):
        path = j.sal.fs.joinPaths(self.path, "ui.python")
        if j.sal.fs.exists(path, followlinks=True):
            return j.sal.fs.fileGetContents(path)
        return ""

    def actorGet(self, aysrepo):
        Actor = self.aysrepo.getActorClass()
        actor = Actor(aysrepo)
        actor.initFromTemplate(template=self)

    def __repr__(self):
        return "actortemplate: %-15s:%s" % (self.domain, self.name)
