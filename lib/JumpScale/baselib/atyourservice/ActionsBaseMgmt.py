from JumpScale import j
import JumpScale.sal.tmux
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


    def input(self, serviceObj):
        """
        gets executed before init happens of this ays
        use this method to manipulate the arguments which are given or already part of ays instance
        this is done as first action on an ays, at central location

        example how to use

        ```
        #call parent, to make sure std init_post is executed
        ActionsBase.init(self,serviceObj)
        if serviceObj.name.startswith("node"):
            args["something"]=111

        ```

        """
        args=serviceObj.args

        toconsume=[]

        def exists(args, name):
            x = name not in args or args[name] is None or args[name] == ""
            return not x

        if serviceObj.name.startswith("node"):
            # set service name & ip addr
            if not exists(args, 'node.tcp.addr') or args['node.tcp.addr'].find('@ask')!=-1:
                if "ip" in args:
                    args['node.tcp.addr'] = args["ip"]

            if not exists(args, 'node.name'):
                args['node.name'] = serviceObj.instance

        if serviceObj.recipe.hrd.getBool("ns.enable",default=False) and "ns" not in serviceObj._producers:

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

        #see if we can find parent if specified (potentially based on role)
        parent=serviceObj.recipe.schema.parentSchemaItemGet()
        if parent!=None:
            #parent exists
            role=parent.parent

            if role in serviceObj.args:
                #has been speficied or empty
                rolearg=serviceObj.args[role].strip()
            else:
                rolearg=""
            if rolearg=="":
                ays_s=j.atyourservice.findServices(role=role)
                if len(ays_s)==1:
                    #we found 1 service of required role, will take that one
                    aysi=ays_s[0]
                    rolearg=aysi.instance
                    serviceObj.args[role]=rolearg
                elif len(ays_s)>1:
                    raise RuntimeError("Cannt find parent with role '%s' for service '%s, there is more than 1"%(role,serviceObj))
                else:
                    if parent.parentauto:
                        j.atyourservice.new(name=parent.parent, instance='main', version='', domain='', path=None, parent=None, args={}, consume='')
                        rolearg="main"
                    else:
                        raise RuntimeError("Cannot find parent with role '%s' for service '%s, there is none, please make sure the service exists."%(role,serviceObj))

            #check we can find
            ays_s=j.atyourservice.findServices(role=role,instance=rolearg)
            if len(ays_s)==1:
                pass
                #all ok
            elif len(ays_s)>1:
                raise RuntimeError("Cannt find parent '%s' for service '%s, there is more than 1 with instance:'%s'"%(role,serviceObj,rolearg))
            else:
                raise RuntimeError("Cannot find parent '%s:%s' for service '%s:%s', please make sure the service exists."%(role,rolearg,serviceObj))

            serviceObj.hrd.set("parent",ays_s[0].shortkey)
            serviceObj._parent=ays_s[0]

        #manipulate the HRD's to mention the consume's to producers
        consumes=serviceObj.recipe.schema.consumeSchemaItemsGet()


        if consumes!=[]:

            for consumeitem in consumes:
                #parent exists
                role=consumeitem.consume_link
                consumename=consumeitem.name

                # if consumename=="parent":
                #     continue

                if not consumename in serviceObj.args:
                    ays_s=[]
                else:
                    ays_s=[]
                    serviceObj.args[consumename]=j.data.text.getList(serviceObj.args[consumename])
                    for instancename in serviceObj.args[consumename]:
                        service=j.atyourservice.getService(role=role,instance=instancename)
                        if service not in ays_s:
                            ays_s.append(service)

                if len(ays_s)>int(consumeitem.consume_nr_max):
                    raise RuntimeError("Found too many services with role '%s' which we are relying upon for service '%s, max:'%s'"%(role,serviceObj,consumeitem.consume_nr_max))
                if len(ays_s)<int(consumeitem.consume_nr_min):
                    msg="Found not enough services with role '%s' which we are relying upon for service '%s, min:'%s'"%(role,serviceObj,consumeitem.consume_nr_min)
                    if len(ays_s)>0:
                        msg+="Require following instances:%s"%serviceObj.args[consumename]
                    raise RuntimeError(msg)

                for ays in ays_s:
                    if role not in  serviceObj.producers:
                        serviceObj._producers[role]=[]
                    if ays not in serviceObj._producers[role]:
                        serviceObj._producers[role].append(ays)


            for key, services in serviceObj._producers.items():
                producers = []
                for service in services:
                    if service.key not in producers:
                        producers.append(service.shortkey)

                serviceObj.hrd.set("producer.%s" % key, producers)






        # if serviceObj.parent!=None:
        #     from IPython import embed
        #     print ("DEBUG NOW 222")
        #     embed()

        #     p

        # from IPython import embed
        # embed()


        # for depkey in serviceObj.recipe.hrd.getList("dependencies.node", default=[]):

        #     # they need to be deployed in host or local (set consumptions)
        #     node = serviceObj.getNode()
        #     res = j.atyourservice.findServices(role=depkey, node=node)
        #     if len(res) == 0:
        #         # not deployed yet
        #         if depkey.find("@")!=0:
        #             depkey="@"+depkey
        #         domain, name, version, instance, role = j.atyourservice.parseKey(depkey)

        #         templ = j.atyourservice.findTemplates(domain=domain, name=name, first=True, role=role)
        #         if instance=="":
        #             instance="main"

        #         serv = templ.newInstance(instance=instance, args={}, parent=node, consume="", originator=serviceObj)  # consume should be configured auto
        #     elif len(res) > 1:
        #         j.events.inputerror_critical("Found more than 1 dependent ays (node), cannot fullfil dependency requirement.\nI am %s, I am trying to depend on %s"%(serviceObj,depkey))
        #     else:
        #         serv = res[0]

        #     serviceObj.consume(serv)

        # for depkey in serviceObj.recipe.hrd.getList("dependencies.global", default=[]):
        #     if depkey.find("@")!=0:
        #         depkey="@"+depkey
        #     if serviceObj.originator is not None and serviceObj.originator._producers != {} and depkey in serviceObj.originator._producers:
        #         res = serviceObj.originator._producers[depkey]
        #     elif serviceObj._producers != {} and depkey in serviceObj._producers:
        #         res = serviceObj._producers[depkey]
        #     else:
        #         domain, name, version, instance, role = j.atyourservice.parseKey(depkey)
        #         res = j.atyourservice.findServices(domain=domain, name=name, instance=instance, role=role)
        #     if len(res) == 0:
        #         j.events.inputerror_critical("Could not find dependency, please install.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
        #     elif len(res) > 1:
        #         j.events.inputerror_critical("Found more than 1 dependent ays (global), please specify, cannot fullfil dependency requirement.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
        #     else:
        #         serv = res[0]

        #     serviceObj.consume(serv)

        return toconsume

    # def consume(self,serviceObj,producer):
    #     pass


    def hrd(self, serviceObj):
        """
        manipulate the hrd's after processing of the @ASK statements
        """
        if "ns" != serviceObj.role and not serviceObj.name.startswith("ns."):
            # means we are not a nameservice ourselves (otherwise chicken & the egg issue)
            serv = j.atyourservice.findServices(role="ns")
            if len(serv) == 1:
                serv = serv[0]
                instance = serviceObj.instance
                name = serviceObj.name.split(".")[0]
                serv.actions_mgmt.register(serv, "%s.%s" % (instance, name))
        return True

    def _searchDep(self, serviceObj, depkey,die=True):
        if serviceObj._producers != {} and depkey in serviceObj._producers:
            dep = serviceObj._producers[depkey]
        else:
            dep = j.atyourservice.findServices(role=depkey)

        if len(dep)==0 and die==False:
            return None
        if len(dep)>1 and die==False:
            return None
        if len(dep) == 0:
            j.events.inputerror_critical("Could not find dependency, please install.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
        elif len(dep) > 1:
            j.events.inputerror_critical("Found more than 1 dependent ays, please specify, cannot fullfil dependency requirement.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
        else:
            serv = dep[0]
        return serv

    # def consume(self, serviceObj, producer):
    #     """
    #     gets executed just before we do install
    #     this allows hrd's to be influeced
    #     """
    #     pass

    # def install_pre(self, serviceObj):
    #     """
    #     """
    #     return True

    # def install_post(self, serviceObj):
    #     """
    #     """
    #     return True

    # def start(self,serviceObj):
    #     """
    #     """
    #     return True

    # def stop(self, serviceObj):
    #     """
    #     """
    #     return True

    # def halt(self,serviceObj):
    #     """
    #     hard kill the app
    #     """
    #     return True

    # def check_up(self, serviceObj, wait=True):
    #     """
    #     do checks to see if process(es) is (are) running.
    #     """
    #     return True

    # def check_down(self, serviceObj, wait=True):
    #     """
    #     do checks to see if process(es) is down.
    #     """
    #     return True


    # def check_requirements(self,serviceObj):
    #     """
    #     do checks if requirements are met to install this app
    #     e.g. can we connect to database, is this the right platform, ...
    #     """
    #     return True

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

    # def monitor(self, serviceObj):
    #     """
    #     monitoring actions
    #     do not forget to schedule in your service.hrd or instance.hrd
    #     """
    #     return True

    # def cleanup(self,serviceObj):
    #     """
    #     regular cleanup of env e.g. remove logfiles, ...
    #     is just to keep the system healthy
    #     do not forget to schedule in your service.hrd or instance.hrd
    #     """
    #     return True

    # def data_export(self,serviceObj):
    #     """
    #     export data of app to a central location (configured in hrd under whatever chosen params)
    #     return the location where to restore from (so that the restore action knows how to restore)
    #     we remember in $name.export the backed up events (epoch,$id,$state,$location)  $state is OK or ERROR
    #     """
    #     return False

    # def data_import(self,id,serviceObj):
    #     """
    #     import data of app to local location
    #     if specifies which retore to do, id corresponds with line item in the $name.export file
    #     """
    #     return False

    # def uninstall(self,serviceObj):
    #     """
    #     uninstall the apps, remove relevant files
    #     """
    #     pass

    # def removedata(self,serviceObj):
    #     """
    #     remove all data from the app (called when doing a reset)
    #     """
    #     pass


    # def test(self,serviceObj):
    #     """
    #     test the service on appropriate behavior
    #     """
    #     pass

    # def build(self, serviceObj):
    #     folders = serviceObj.installRecipe()

    #     for src, dest in folders:
    #         serviceObj.upload2AYSfs(dest)
