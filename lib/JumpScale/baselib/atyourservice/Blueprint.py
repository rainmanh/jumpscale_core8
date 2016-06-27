from JumpScale import j

CATEGORY = "ays:bp"


def log(msg, level=2):
    j.logger.log(msg, level=level, category=CATEGORY)


class Blueprint:
    """
    """

    def __init__(self, aysrepo, path="", content=""):
        self.aysrepo = aysrepo
        self.path = path
        self.active=True
        if path != "":
            self.name = j.sal.fs.getBaseName(path)
            if self.name[0]=="_":
                self.active=False 
            self.name = self.name.lstrip('_')
            self.content = j.sal.fs.fileGetContents(path)
        else:
            self.name = 'unknown'
            self.content = content

        self.models = []
        self._contentblocks = []

        content = ""

        nr = 0
        # we need to do all this work because the yaml parsing does not maintain order because its a dict
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
                        raise j.exceptions.Input("Key in blueprint is not right format, needs to be $aysname__$instance, found:'%s'" % key)
                    aysname, aysinstance = key.lower().split("__", 1)

                    if instance != "" and aysinstance != instance:
                        log("ignore load from blueprint for: %s:%s" % (aysname, aysinstance))
                        continue

                    if aysname.find(".") != -1:
                        rolefound, _ = aysname.split(".", 1)
                    else:
                        rolefound = aysname

                    if role != "" and role != rolefound:
                        log("ignore load from blueprint based on role for: %s:%s" % (aysname, aysinstance))
                        continue

                    recipe = self.aysrepo.getRecipe(aysname, die=False)

                    if recipe is None:
                        # check if its a blueprintays, if yes then template name is different
                        aystemplate_name = aysname
                        if not aysname.startswith('blueprint.'):
                            blueaysname = 'blueprint.%s' % aysname
                            if self.aysrepo.existsTemplate(blueaysname):
                                aystemplate_name = blueaysname

                        recipe = self.aysrepo.getRecipe(aystemplate_name)  # will load recipe if it doesn't exist yet

                    aysi = recipe.newInstance(instance=aysinstance, args=item)

    def _add2models(self, content, nr):
        # make sure we don't process double
        if content in self._contentblocks:
            return
        self._contentblocks.append(content)
        try:
            model = j.data.serializer.yaml.loads(content)
        except Exception as e:
            msg = "Could not process blueprint (load from yaml):\npath:'%s',\nline: '%s', content:\n######\n\n%s\n######\nerror:%s" % (self.path, nr, content, e)
            raise j.exceptions.Input(msg)

        self.models.append(model)

    @property
    def services(self):
        services = []
        for model in self.models:
            if model is not None:
                for key, item in model.items():
                    if key.find("__") == -1:
                        raise j.exceptions.Input("Key in blueprint is not right format, needs to be $aysname__$instance, found:'%s'" % key)

                    aysname, aysinstance = key.lower().split("__", 1)
                    if aysname.find(".") != -1:
                        rolefound, _ = aysname.split(".", 1)
                    else:
                        rolefound = aysname

                    service = self.aysrepo.getService(role=rolefound, instance=aysinstance, die=False)
                    if service:
                        services.append(service)

        return services

    def disable(self):
        if self.active:
            base=j.sal.fs.getBaseName(self.path)
            dirpath=j.sal.fs.getDirName(self.path)
            newpath=j.sal.fs.joinPaths(dirpath,"_%s"%base)
            j.sal.fs.moveFile(self.path,newpath)
            self.path=newpath
            self.active=False

    def enable(self):
        if self.active==False:
            base=j.sal.fs.getBaseName(self.path)
            if base.startswith("_"):
                base=base[1:]
            dirpath=j.sal.fs.getDirName(self.path)
            newpath=j.sal.fs.joinPaths(dirpath,base)
            j.sal.fs.moveFile(self.path,newpath)
            self.path=newpath
            self.active=True

    def __str__(self):
        return "%s:%s" % (self.name, self.hash)

    __repr__ = __str__
