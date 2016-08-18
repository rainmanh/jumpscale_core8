

from JumpScale import j

from JumpScale.baselib.atyourservice.Service import *


class ActorBase:

    def _init_props(self):

        self._hrd = None
        self._schema_actor = None
        self._schema_service = None
        self._schema_actor_capnp = None
        self._schema_service_capnp = None
        self._actions = None
        self._mongoModel = None

        self.path_hrd_actor = j.sal.fs.joinPaths(self.path, "actor.hrd")
        self._path_actions = j.sal.fs.joinPaths(self.path, "actions.py")
        self.path_hrd_schema_actor = j.sal.fs.joinPaths(self.path, "schema_actor.hrd")
        self.path_hrd_schema_service = j.sal.fs.joinPaths(self.path, "schema.hrd")
        self.path_capnp_schema_actor = j.sal.fs.joinPaths(self.path, "actor.capnp")
        self.path_capnp_schema_service = j.sal.fs.joinPaths(self.path, "service.capnp")
        self.path_mongo_model = j.sal.fs.joinPaths(self.path, "model.py")

        self.role = self.name.split('.')[0]

    def __str__(self):
        return self.__repr__()


class ActorTemplate(ActorBase):

    def __init__(self, gitrepo, path, aysrepo=None):

        # path is path in gitrepo or absolute path

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

        self._init_props()

    @property
    def schemaActor(self):
        if self._schema_actor == "EMPTY":
            return None
        if self._schema_actor == None:
            if not j.sal.fs.exists(self.path_hrd_schema_actor):
                self._schema_actor = "EMPTY"
            else:
                self._schema_actor = j.data.hrd.getSchema(self.path_hrd_schema_actor)
        return self._schema_actor

    @property
    def schemaService(self):
        if self._schema_service == "EMPTY":
            return None
        if self._schema_service == None:
            if not j.sal.fs.exists(self.path_hrd_schema_service):
                self._schema_service = "EMPTY"
            else:
                self._schema_service = j.data.hrd.getSchema(self.path_hrd_schema_service)
        return self._schema_service

    @property
    def hrd(self):
        if self._hrd == "EMPTY":
            return None
        if self._hrd is not None:
            return self._hrd
        hrdpath = self.path_hrd_actor
        if not j.sal.fs.exists(hrdpath):
            # check if we can find it in other ays template
            if self.name.find(".") != -1:
                name0 = self.name.split(".", 1)[0]
                templ = j.atyourservice.actorTemplateGet(name=name0, die=False)
                if templ is not None:
                    self._hrd = templ._hrd
                    self.path_hrd_actor = templ.path_hrd_actor
                    return self._hrd
                else:
                    self._hrd == "EMPTY"
                    return None
        if j.sal.fs.exists(hrdpath):
            self._hrd = j.data.hrd.get(hrdpath, prefixWithName=False)
        else:
            self._hrd = "EMPTY"
            return None
        return self._hrd

    @property
    def model_mongo(self):
        if self._mongoModel is None:
            if j.sal.fs.exists(self.path_mongo_model):
                modulename = "JumpScale.atyourservice.%s.%s.model" % (
                    self.domain, self.name)
                mod = loadmodule(modulename, self.path_mongo_model)
                self._mongoModel = mod.Model()
        return self._mongoModel

    def actorGet(self, aysrepo):
        from JumpScale.baselib.atyourservice.Actor import Actor
        return Actor(aysrepo, template=self)

    def __repr__(self):
        return "actortemplate: %-15s:%s" % (self.domain, self.name)
