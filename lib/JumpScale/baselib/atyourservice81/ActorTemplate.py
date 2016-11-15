

from JumpScale import j

from collections import OrderedDict

# don't work with properties, this only happens when init is asked for so no big deal for performance


class ActorTemplate():

    def __init__(self, gitrepo, path, aysrepo=None):

        # path is path in gitrepo or absolute path
        self.logger = j.atyourservice.logger
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
    def role(self):
        return self.name.split('.')[0]

    @property
    def remoteUrl(self):
        git = j.clients.git.get(self.path, False)
        return git.remoteUrl

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
                self._schemaHrd = j.data.hrd.getSchema(content="")
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
                res = j.atyourservice.actorTemplatesFind(name=name0)
                if len(res) == 1:
                    return res[0].hrd
                elif len(res) > 1:
                    raise j.exceptions.RuntimeError('Found more then one actor template with name %s' % name)
            return j.data.hrd.get(content="")

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

    @property
    def recurringDict(self):
        return self._hrd.getDictFromPrefix('recurring')

    @property
    def eventDict(self):
        return self._hrd.getDictFromPrefix('event')

    def actorGet(self, aysrepo):
        Actor = self.aysrepo.getActorClass()
        actor = Actor(aysrepo)
        actor.initFromTemplate(template=self)

    @property
    def flists(self):
        flists = self._hrd.getDictFromPrefix('flists')
        for name in list(flists.keys()):
            path = j.sal.fs.joinPaths(self.path, 'flists', name)
            if j.sal.fs.exists(path):
                flists[name]['content'] = j.sal.fs.fileGetContents(path)
            elif j.sal.fs.exists(path + '.flist'):
                flists[name]['content'] = j.sal.fs.fileGetContents(path + '.flist')
            else:
                raise j.exceptions.NotFound("flist definition in %s references a file that doesn't exists: %s" % (self, path))

        return flists

    def __repr__(self):
        return "actortemplate: %-15s:%s" % (self.domain, self.name)
