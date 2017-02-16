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
        self.models = []  # can be actions or services or recurring
        self.actions = []
        self.eventFilters = []
        self._contentblocks = []


        if path != "":
            self.name = j.sal.fs.getBaseName(path)
            if self.name[0] == "_":
                self.active = False
            self.name = self.name.lstrip('_')
            self.content = j.sal.fs.fileGetContents(path)
        else:
            self.name = 'unknown'
            self.content = content

        self.is_valid = self._validate_yaml(self.content)

        if self.is_valid:
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

            self.is_valid = self._validate_format(self.models)

    async def load(self, role="", instance=""):
        self.actions = []
        self.eventFilters = []
        for model in self.models:
            if model is not None:

                if "actions" in model:
                    # found action need to add them to blueprint
                    for actionModel in model["actions"]:
                        if 'actor' not in actionModel:
                            actor0 = ""
                        else:
                            actor0 = actionModel["actor"]
                        if 'service' not in actionModel:
                            service0 = ""
                        else:
                            service0 = actionModel["service"]
                        if 'recurring' not in actionModel:
                            recurring0 = ""
                        else:
                            recurring0 = actionModel["recurring"]
                        servicesFound = self.aysrepo.servicesFind(name=service0, actor=actor0)

                        if len(servicesFound) == 0:
                            self.logger.error("found action to execute but could not find required service:%s!%s" % (actor0, service0))
                            continue

                        if "action" not in actionModel:
                            raise j.exceptions.Input(message="need to specify action.",
                                                     level=1, source="", tags="", msgpub="")

                        actions = [item.strip() for item in actionModel["action"].split(",") if item.strip() != ""]

                        for serviceObj in servicesFound:
                            for actionName in actions:
                                self.actions.append({
                                    'service_key': serviceObj.model.key,
                                    'action_name': actionName,
                                    'recurring_period': recurring0,
                                })

                elif "eventfilters" in model:
                        # found action need to add them to blueprint
                    for obj in model["eventfilters"]:
                        if 'actor' not in obj:
                            actor0 = ""
                        else:
                            actor0 = obj["actor"]
                        if 'service' not in obj:
                            service0 = ""
                        else:
                            service0 = obj["service"]
                        if 'channel' not in obj:
                            channel0 = ""
                        else:
                            channel0 = obj["channel"]
                        if 'command' not in obj:
                            cmd0 = ""
                        else:
                            cmd0 = obj["command"]
                        if 'secret' not in obj:
                            secret0 = ""
                        else:
                            secret0 = obj["secret"]
                        if 'actions' not in obj:
                            action0 = []
                        else:
                            action0 = obj["actions"]

                        servicesFound = self.aysrepo.servicesFind(name=service0, actor=actor0)

                        if len(servicesFound) == 0:
                            raise j.exceptions.Input(message="found action to execute but could not find required service:%s!%s" % (
                                actor0, service0), level=1, source="", tags="", msgpub="")

                        for serviceObj in servicesFound:
                            self.eventFilters.append({
                                'service_key': serviceObj.model.key,
                                'channel': channel0,
                                'command': cmd0,
                                'secret': secret0,
                                'action_name': action0,
                            })

                else:
                    for key, item in model.items():
                        if key.find("__") == -1:
                            raise j.exceptions.Input(
                                "Key in blueprint is not right format, needs to be $aysname__$instance, found:'%s'" % key)
                        actorname, bpinstance = key.split("__", 1)

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

                        actor = self.aysrepo.actorGet(actorname)
                        args = {} if item is None else item
                        await actor.serviceCreate(instance=bpinstance, args=args)

        # first we had to make sure all services do exist, then we can add these properties
        for action_info in self.actions:
            service = self.aysrepo.serviceGetByKey(action_info['service_key'])
            service.scheduleAction(action_info['action_name'], period=action_info['recurring_period'])
            service.saveAll()

        for event_filter in self.eventFilters:
            service = self.aysrepo.serviceGetByKey(event_filter['service_key'])
            service.model.eventFilterSet(
                channel=event_filter['channel'], actions=event_filter['action_name'],
                command=event_filter['command'], secrets=event_filter['secret'])
            service.saveAll()

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
                for key in model.keys():

                    aysname, aysinstance = key.split("__", 1)
                    if aysname.find(".") != -1:
                        rolefound, _ = aysname.split(".", 1)
                    else:
                        rolefound = aysname

                    service = self.aysrepo.serviceGet(role=rolefound, instance=aysinstance, die=False)
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
        if self.active is False:
            base = j.sal.fs.getBaseName(self.path)
            if base.startswith("_"):
                base = base[1:]
            dirpath = j.sal.fs.getDirName(self.path)
            newpath = j.sal.fs.joinPaths(dirpath, base)
            j.sal.fs.moveFile(self.path, newpath)
            self.path = newpath
            self.active = True

    def _validate_yaml(self, content):
        try:
            j.data.serializer.yaml.loads(content)
            return True
        except yaml.YAMLError:
            raise j.exceptions.Input('Yaml format is not valid for %s please fix this to continue' % self.name)

    def _validate_format(self, models):
        for model in models:
            if model is None:
                continue

            if model and not j.data.types.dict.check(model):
                self.logger.error("Bad formatted blueprint: %s" % self.path)
                return False

            for key in model.keys():

                # this two blocks doesn't have the same format as classic service declaration
                if key in ['actions', 'eventfilters']:
                    if not j.data.types.list.check(model[key]):
                        self.logger.error("%s should be a list of dictionary: found %s" % (key, type(model[key])))
                        return False
                else:
                    if key.find("__") == -1:
                        self.logger.error("Key in blueprint is not right format, needs to be $aysname__$instance, found:'%s'" % key)
                        return False

                    aysname, _ = key.split("__", 1)
                    if aysname not in self.aysrepo.templates:
                        self.logger.error("Service template %s not found. Can't execute this blueprint" % aysname)
                        return False

        return True

    def validate(self):
        if not self._validate_yaml(self.content):
            return False

        if not self._validate_format(self.models):
            return False

        return True

    def __str__(self):
        return "%s:%s" % (self.name, self.hash)

    __repr__ = __str__
