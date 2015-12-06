from JumpScale import j
import JumpScale.sal.screen
import os
import signal
import inspect

CATEGORY = "atyourserviceActionNode"

def log(msg, level=2):
    j.logger.log(msg, level=level, category=CATEGORY)


class ActionsBaseMgmt(object):
    """
    implement methods of this class to change behavior of lifecycle management of service
    this one happens at central side from which we coordinate our efforts
    """

    def init(self, serviceObj, args):
        """
        gets executed before init happens of this ays
        use this method to manipulate the arguments which are given or already part of ays instance
        this is done as first action on an ays, even at central location

        example how to use

        ```
        #call parent, to make sure std init_post is executed
        ActionsBase.init(self,serviceObj,hrd,args)
        if serviceObj.name.startswith("node"):
            args["something"]=111

        ```
        important: only modify the hrd & the args !!!

        """
        # print "init:%s"%serviceObj

        toconsume=[]

        def exists(args, name):
            x = name not in args or args[name] is None or args[name] == ""
            return not x

        if serviceObj.name.startswith("node"):
            # set service name & ip addr
            if not exists(args, 'node.tcp.addr') or args['node.tcp.addr'].startswith('@ASK'):
                if "ip" in args:
                    args['node.tcp.addr'] = args["ip"]

            if not exists(args, 'node.name'):
                args['node.name'] = serviceObj.instance

        # # check if 1 of parents is of type node
        # for parent in serviceObj.parents:
        #     if parent.role=="node":#.startswith("node"):
        #         serviceObj.consume(serviceObj.parent)
        #         args['tcp.addr'] = serviceObj.parent.hrd.get('node.tcp.addr')
        #         break

        if serviceObj.template.hrd_template.getBool("ns.enable",default=False) and "ns" not in serviceObj._producers:

            if "ns" != serviceObj.role and not serviceObj.name.startswith("ns."):
                # means we are not a nameservice ourselves (otherwise chicken & the egg issue)
                serv = j.atyourservice.findServices(role="ns")
                if len(serv) == 1:
                    ns_service = serv[0]
                    serviceObj.consume("@ns")

                    nsinstance = serviceObj.instance
                    nsname = serviceObj.name.split(".")[0]
                    nsdomain = ns_service.hrd.get("instance.ns.domain")
                    if "instance.dns" not in args:
                        args["instance.dns"] = []
                    args["instance.dns"].append("%s.%s.%s" % (nsinstance, nsname, nsdomain))

        for depkey in serviceObj.template.hrd_template.getList("dependencies.node", default=[]):

            # they need to be deployed in host or local (set consumptions)
            node = serviceObj.getNode()
            res = j.atyourservice.findServices(role=depkey, node=node)
            if len(res) == 0:
                # not deployed yet
                if depkey.find("@")!=0:
                    depkey="@"+depkey
                domain, name, version, instance, role = j.atyourservice.parseKey(depkey)

                templ = j.atyourservice.findTemplates(domain=domain, name=name, first=True, role=role)
                if instance=="":
                    instance="main"

                serv = templ.newInstance(instance=instance, args={}, parent=node, consume="", originator=serviceObj)  # consume should be configured auto
            elif len(res) > 1:
                j.events.inputerror_critical("Found more than 1 dependent ays (node), cannot fullfil dependency requirement.\nI am %s, I am trying to depend on %s"%(serviceObj,depkey))
            else:
                serv = res[0]

            serviceObj.consume(serv)

        for depkey in serviceObj.template.hrd_template.getList("dependencies.global", default=[]):
            if depkey.find("@")!=0:
                depkey="@"+depkey
            if serviceObj.originator is not None and serviceObj.originator._producers != {} and depkey in serviceObj.originator._producers:
                res = serviceObj.originator._producers[depkey]
            elif serviceObj._producers != {} and depkey in serviceObj._producers:
                res = serviceObj._producers[depkey]
            else:
                domain, name, version, instance, role = j.atyourservice.parseKey(depkey)
                res = j.atyourservice.findServices(domain=domain, name=name, instance=instance, role=role)
            if len(res) == 0:
                j.events.inputerror_critical("Could not find dependency, please install.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
            elif len(res) > 1:
                j.events.inputerror_critical("Found more than 1 dependent ays (global), please specify, cannot fullfil dependency requirement.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
            else:
                serv = res[0]

            serviceObj.consume(serv)

        return toconsume

    def consume(self, serviceObj, producer):
        """
        gets executed just before we do install
        this allows hrd's to be influeced
        """
        pass


    def configure(self,serviceObj):
        """
        this gets executed after the files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the service if anything needs to be started

        @return if you return "r" then system will restart after configure, otherwise return True if ok. False if not.

        """

        if "ns" != serviceObj.role and not serviceObj.name.startswith("ns."):
            # means we are not a nameservice ourselves (otherwise chicken & the egg issue)
            serv = j.atyourservice.findServices(role="ns")
            if len(serv) == 1:
                serv = serv[0]
                instance = serviceObj.instance
                name = serviceObj.name.split(".")[0]
                serv.actions.register(serv, "%s.%s" % (instance, name))

        return True


    # def _getDomainName(self, serviceObj, process):
    #     domain=serviceObj.domain
    #     if process["name"]!="":
    #         name=process["name"]
    #     else:
    #         name=serviceObj.name
    #         if serviceObj.instance!="main":
    #             name+="__%s"%serviceObj.instance
    #     return domain, name


    def start(self,serviceObj):
        """
        """
        return True

    def stop(self, serviceObj):
        """
        """
        return True

    def halt(self,serviceObj):
        """
        hard kill the app
        """
        return True

    def check_up(self, serviceObj, wait=True):
        """
        do checks to see if process(es) is (are) running.
        """
        return True

    def check_down(self, serviceObj, wait=True):
        """
        do checks to see if process(es) is down.
        """
        return True


    def check_requirements(self,serviceObj):
        """
        do checks if requirements are met to install this app
        e.g. can we connect to database, is this the right platform, ...
        """
        return True

    # def schedule(self, serviceObj, cron, method):
    #     """
    #     Schedules a method call according to cron

    #     :param serviceObj: the Service Object
    #     :param cron: cron spec (syntax is as defined in https://en.wikipedia.org/wiki/Cron)
    #     :param method: Function to be scheduled. Make sure the function should not depend on any context or state
    #                  attributes because it will get executed remotely on the agent.
    #     """
    #     if not inspect.isfunction(method):
    #         raise ValueError("Only 'functions' are supported (no class methods)")
    #     client = j.clients.ac.get()
    #     cron_id = 'ays.{name}.{method}'.format(name=str(serviceObj), method=method.__name__)

    #     # find agent for this service node.
    #     agents = j.atyourservice.findServices(name='agent2', parent=serviceObj.parent)

    #     if serviceObj.parent is None:
    #         agents = filter(lambda a: a.parent is None, agents)

    #     assert len(agents) == 1, \
    #         'Can not find the agent instance for service %s. found %s matching agents' % (serviceObj, len(agents))

    #     agent = agents[0]
    #     gid = agent.hrd.get('gid')
    #     nid = agent.hrd.get('nid')

    #     tags = j.data.tags.getTagString(labels={'ays', 'monitor'}, tags={'service': str(serviceObj)})
    #     client.scheduler.executeJumpscript(cron_id, cron, method=method, gid=gid, nid=nid, tags=tags)

    # def unschedule(self, serviceObj):
    #     """
    #     Unschedules all crons created by the schedule method.
    #     """
    #     try:
    #         client = j.clients.ac.get()
    #     except Exception, err:
    #         log("WARNING: Failed to unschedule monitor tasks for '%s' due to '%s'" % (serviceObj, err))
    #         return

    #     prefix = 'ays.{name}.'.format(name=str(serviceObj))
    #     client.scheduler.unschedule_prefix(prefix)

    def monitor(self, serviceObj):
        """
        monitoring actions
        do not forget to schedule in your service.hrd or instance.hrd
        """
        return True

    def cleanup(self,serviceObj):
        """
        regular cleanup of env e.g. remove logfiles, ...
        is just to keep the system healthy
        do not forget to schedule in your service.hrd or instance.hrd
        """
        return True

    def data_export(self,serviceObj):
        """
        export data of app to a central location (configured in hrd under whatever chosen params)
        return the location where to restore from (so that the restore action knows how to restore)
        we remember in $name.export the backed up events (epoch,$id,$state,$location)  $state is OK or ERROR
        """
        return False

    def data_import(self,id,serviceObj):
        """
        import data of app to local location
        if specifies which retore to do, id corresponds with line item in the $name.export file
        """
        return False

    def uninstall(self,serviceObj):
        """
        uninstall the apps, remove relevant files
        """
        pass

    def removedata(self,serviceObj):
        """
        remove all data from the app (called when doing a reset)
        """
        pass


    def test(self,serviceObj):
        """
        test the service on appropriate behavior
        """
        pass


