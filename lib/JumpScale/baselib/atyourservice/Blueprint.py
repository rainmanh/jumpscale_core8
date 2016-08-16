from JumpScale import j
import yaml

CATEGORY = "ays:bp"


class Blueprint:
    """
    """

    def __init__(self, aysrepo, path="", content=""):
        self.logger = j.logger.get('j.atyourservice.blueprint')
        self.aysrepo = aysrepo
        self.path = path
        self.active = True
        if path != "":
            self.name = j.sal.fs.getBaseName(path)
            if self.name[0] == "_":
                self.active = False
            self.name = self.name.lstrip('_')
            self.content = j.sal.fs.fileGetContents(path)
        else:
            self.name = 'unknown'
            self.content = content

        try:
            j.data.serializer.yaml.loads(self.content)
        except yaml.YAMLError:
            msg = 'Yaml format of the blueprint is not valid.'
            raise j.exceptions.Input(message=msg, msgpub=msg)

        self.models = []
        self._contentblocks = []

        content = ""

        nr = 0
        # we need to do all this work because the yaml parsing does not
        # maintain order because its a dict
        for line in self.content.split("\n"):
            if len(line) > 0 and line[0] == "#":
                continue
            if content == "" and line.strip() == "":
                continue

            line = line.replace("\t", "    ")
            nr += 1
            if len(content) > 0 and (len(line) > 0 and line[0] != " "):
                self._add2models(content, nr)
                content = ""

            content += "%s\n" % line

        # to process the last one
        self._add2models(content, nr)
        self._contentblocks = []

        self.hash = j.data.hash.md5_string(self.content)

    def load(self, role="", instance=""):
        for model in self.models:
            if model is not None:
                for key, item in model.items():
                    if key.find("__") == -1:
                        raise j.exceptions.Input(
                            "Key in blueprint is not right format, needs to be $aysname__$instance, found:'%s'" % key)
                    actorname, bpinstance = key.lower().split("__", 1)

                    if instance != "" and bpinstance != instance:
                        self.logger.info(
                            "ignore load from blueprint for: %s:%s" % (actorname, bpinstance))
                        continue

                    if actorname.find(".") != -1:
                        rolefound, _ = actorname.split(".", 1)
                    else:
                        rolefound = actorname

                    if role != "" and role != rolefound:
                        self.logger.info(
                            "ignore load from blueprint based on role for: %s:%s" % (actorname, bpinstance))
                        continue

                    # check if we can find actorname and if not then check if there is a blueprint.  name...
                    if not self.aysrepo.templateExists(actorname) and not actorname.startswith('blueprint.'):
                        blueaysname = 'blueprint.%s' % actorname
                        if self.aysrepo.templateExists(blueaysname):
                            actorname = blueaysname

                    if not self.aysrepo.templateExists(actorname):
                        raise j.exceptions.Input(message="Cannot find actor:%s" %
                                                 actorname, level=1, source="", tags="", msgpub="")

                    actor = self.aysrepo.actorGet(actorname, reload=True)

                    if not len(self.aysrepo.servicesFind(role=actor.role, instance=bpinstance)):
                        # if it's not there, create it.
                        aysi = actor.serviceCreate(
                            instance=bpinstance, args=item)

    def _add2models(self, content, nr):
        # make sure we don't process double
        if content in self._contentblocks:
            return
        self._contentblocks.append(content)
        try:
            model = j.data.serializer.yaml.loads(content)
        except Exception as e:
            msg = "Could not process blueprint (load from yaml):\npath:'%s',\nline: '%s', content:\n######\n\n%s\n######\nerror:%s" % (
                self.path, nr, content, e)
            raise j.exceptions.Input(msg)

        self.models.append(model)

    @property
    def services(self):
        services = []
        for model in self.models:
            if model is not None:
                for key, item in model.items():
                    if key.find("__") == -1:
                        raise j.exceptions.Input(
                            "Key in blueprint is not right format, needs to be $aysname__$instance, found:'%s'" % key)

                    aysname, aysinstance = key.lower().split("__", 1)
                    if aysname.find(".") != -1:
                        rolefound, _ = aysname.split(".", 1)
                    else:
                        rolefound = aysname

                    service = self.aysrepo.getService(
                        role=rolefound, instance=aysinstance, die=False)
                    if service:
                        services.append(service)

        return services

    def disable(self):
        if self.active:
            base = j.sal.fs.getBaseName(self.path)
            dirpath = j.sal.fs.getDirName(self.path)
            newpath = j.sal.fs.joinPaths(dirpath, "_%s" % base)
            j.sal.fs.moveFile(self.path, newpath)
            self.path = newpath
            self.active = False

    def enable(self):
        if self.active == False:
            base = j.sal.fs.getBaseName(self.path)
            if base.startswith("_"):
                base = base[1:]
            dirpath = j.sal.fs.getDirName(self.path)
            newpath = j.sal.fs.joinPaths(dirpath, base)
            j.sal.fs.moveFile(self.path, newpath)
            self.path = newpath
            self.active = True

    def validate(self):
        for model in self.models:
            if model is not None:
                for key, item in model.items():
                    if key.find("__") == -1:
                        self.logger.error(
                            "Key in blueprint is not right format, needs to be $aysname__$instance, found:'%s'" % key)
                        return False

                    aysname, aysinstance = key.lower().split("__", 1)
                    if aysname not in self.aysrepo.templates:
                        self.logger.error(
                            "Service template %s not found. Can't execute this blueprint" % aysname)
                        return False
        return True

    def __str__(self):
        return "%s:%s" % (self.name, self.hash)

    __repr__ = __str__
