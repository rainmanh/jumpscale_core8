from JumpScale import j
from JumpScale.baselib.atyourservice81.Service import Service
import capnp
import msgpack
from JumpScale.baselib.atyourservice81 import model_capnp as ModelCapnp


class Actor():

    def __init__(self, aysrepo, template=None, model=None):
        """
        init from a template or from a model
        """

        self.aysrepo = aysrepo
        self.logger = j.atyourservice.logger
        self._schema = None
        self.model = None

        if template is not None:
            self._initFromTemplate(template)
        elif model is not None:
            self.model = model
        else:
            raise j.exceptions.Input(
                message="template or model or name needs to be specified when creating an actor", level=1, source="", tags="", msgpub="")

    @property
    def path(self):
        return j.sal.fs.joinPaths(self.aysrepo.path, "actors", self.model.name)

    def saveAll(self):
        self.model.save()
        from IPython import embed
        print("DEBUG NOW save")
        embed()
        raise RuntimeError("stop debug here")

    def processChange(self, changeCategory):
        """
        template action change
        categories :
            - dataschema
            - ui
            - config
            - action_new_actionname
            - action_mod_actionname
            - action_del_actionname
        """
        # self.logger.debug('process change for %s (%s)' % (self, changeCategory))
        if changeCategory == 'dataschema':
            # TODO
            pass

        elif changeCategory == 'ui':
            # TODO
            pass

        elif changeCategory == 'config':
            # TODO
            pass

        elif changeCategory.find('action_new') != -1:
            # TODO
            pass
        elif changeCategory.find('action_mod') != -1:
            # TODO
            pass
        elif changeCategory.find('action_del') != -1:
            action_name = changeCategory.split('action_del_')[1]
            self.model.actionDelete(action_name)

        self.saveAll()

        for service in self.aysrepo.servicesFind(actor=self.model.name):
            service.processChange(actor=self, changeCategory=changeCategory)

# SERVICE

    def serviceCreate(self, instance="main", args={}):
        instance = instance
        service = self.aysrepo.serviceGet(role=self.model.role, instance=instance, die=False)
        if service is not None:
            service._check_args(self, args)
            return service

        # checking if we have the service on the file system
        target = "%s!%s" % (self.model.name, instance)
        services_dir = j.sal.fs.joinPaths(self.aysrepo.path, 'services')
        results = j.sal.fs.walkExtended(services_dir, files=False, dirPattern=target)
        if len(results) > 1:
            raise j.exceptions.RuntimeError("found more then one service directory for %s" % target)
        elif len(results) == 1:
            service = Service(aysrepo=self.aysrepo, path=results[0])
        else:
            service = Service(aysrepo=self.aysrepo, actor=self, name=instance, args=args)

        return service

    @property
    def services(self):
        """
        return a list of instance name for this template
        """
        return self.aysrepo.servicesFind(actor=self.model.dbobj.name)


# GENERIC
    def __repr__(self):
        return "actor: %-15s" % (self.model.name)

    # def loadFromFS(self, name):
    #     """
    #     get content from fs and load in object
    #     """
    #     if self.model is None:
    #         self.model = self.aysrepo.db.actors.new()
    #
    #     actor_path = j.sal.fs.joinPaths(self.aysrepo.path, "actors", name)
    #     self.logger.debug("load actor from FS: %s" % actor_path)
    #     json = j.data.serializer.json.load(j.sal.fs.joinPaths(actor_path, "actor.json"))
    #
    #     # for now we don't reload the actions codes.
    #     # when using distributed DB, the actions code could still be available
    #     del json['actions']
    #     self.model.dbobj = ModelCapnp.Actor.new_message(**json)
    #
    #     # need to save already here cause processActionFile is doing a find
    #     # and it need to be able to find this new actor model we are creating
    #     self.model.save()
    #
    #     # recreate the actions code from the action.py file from the file system
    #     self._processActionsFile(j.sal.fs.joinPaths(actor_path, "actions.py"))
    #
    #     self.saveAll()
    #
    # def saveToFS(self):
    #     j.sal.fs.createDir(self.path)
    #
    #     path = j.sal.fs.joinPaths(self.path, "actor.json")
    #     j.sal.fs.writeFile(filename=path, contents=str(self.model.dictJson), append=False)
    #
    #     actionspath = j.sal.fs.joinPaths(self.path, "actions.py")
    #     j.sal.fs.writeFile(actionspath, self.model.actionsSourceCode)
    #
    #     # path3 = j.sal.fs.joinPaths(self.path, "config.json")
    #     # if self.model.data != {}:
    #     #     j.sal.fs.writeFile(path3, self.model.dataJSON)
    #
    #     path4 = j.sal.fs.joinPaths(self.path, "schema.capnp")
    #     if self.model.dbobj.serviceDataSchema.strip() != "":
    #         j.sal.fs.writeFile(path4, self.model.dbobj.serviceDataSchema)
