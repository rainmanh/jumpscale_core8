

from JumpScale import j

from JumpScale.baselib.atyourservice.Service import *


class ActorTemplate:

    def __init__(self, gitrepo, path):

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

        self.domain = j.sal.fs.getBaseName(gitrepo.baseDir)

        if not self.domain.startswith("ays_"):
            raise j.exceptions.Input(
                "name of ays template git repo should start with ays_, now:%s" % gitrepo.baseDir)

        self.domain = self.domain[4:]

        self._init_props()

    def _init_props(self):

        self._hrd = None
        self._schema = None
        self._actions = None
        self._mongoModel = None
        self._capnpSchema = None

        self.path_hrd_template = j.sal.fs.joinPaths(self.path, "service.hrd")
        self.path_hrd_schema = j.sal.fs.joinPaths(self.path, "schema.hrd")
        self.path_actions = j.sal.fs.joinPaths(self.path, "actions.py")
        self.path_actions_node = j.sal.fs.joinPaths(
            self.path, "actions_node.py")
        self.path_mongo_model = j.sal.fs.joinPaths(self.path, "model.py")
        self.path_capnp_schema = j.sal.fs.joinPaths(self.path, "model.capnp")

        self.role = self.name.split('.')[0]

    @property
    def hrd(self):
        if self._hrd == "EMPTY":
            return None
        if self._hrd is not None:
            return self._hrd
        hrdpath = self.path_hrd_template
        if not j.sal.fs.exists(hrdpath):
            # check if we can find it in other ays template
            if self.name.find(".") != -1:
                name0 = self.name.split(".", 1)[0]
                templ = j.atyourservice.templateGet(name=name0, die=False)
                if templ is not None:
                    self._hrd = templ._hrd
                    self.path_hrd_template = templ.path_hrd_template
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
    def schema(self):
        if self._schema == "EMPTY":
            return None
        if self._schema:
            return self._schema
        hrdpath = self.path_hrd_schema
        if not j.sal.fs.exists(hrdpath):
            self._schema = "EMPTY"
            return None
        self._schema = j.data.hrd.getSchema(hrdpath)
        return self._schema

    @property
    def schema_capnp(self):
        if self._capnpSchema is None:
            if j.sal.fs.exists(self.path_capnp_schema):
                from IPython import embed
                print("DEBUG NOW implement schema capnp")
                embed()
                self._capnpSchema = ""
        return self._capnpSchema

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
        return "template: %-15s:%s" % (self.domain, self.name)

    def __str__(self):
        return self.__repr__()
