
from JumpScale import j
import colored_traceback
colored_traceback.add_hook(always=True)
import functools
import sys

class ActionMethodDecorator:

    def __init__(self,action=True,actionshow=True,actionMethodName="",queue=""):
        self.action=action
        self.actionshow=actionshow
        self.name=actionMethodName

    def __call__(self, func):

        def wrapper(that, *args, **kwargs):

            #this makes sure we show the action on terminal
            if "actionshow" in kwargs:
                actionshow=kwargs.pop("actionshow")
            else:
                actionshow=self.actionshow

            if "action" in kwargs:
                action=kwargs.pop("action")
            else:
                action=self.action

            if "force" in kwargs:
                raise RuntimeError("no longer force ")
                
            # if "force" in kwargs:
            #     force=kwargs.pop("force")
            # else:
            #     force=self.force
            # force=True #because we now have the aysrun so we know what to do and what not

            if "die" in kwargs:
                die = kwargs.pop('die')
            else:
                die = True

            if self.name=="":
                self.name=func.__name__

            # print ("ACTION:START: isaction=%s"%action)

            if 'service' in kwargs:
                if self.name in ['init', 'input']:
                    #will just execute with service as argument
                    action = False
                    service = kwargs['service']
                else:
                    dargs = {}
                    if j.data.types.string.check(kwargs['service']):
                        aysikey = kwargs['service']
                        service = j.atyourservice.getService[aysikey]
                    else:
                        service = kwargs['service']
                        aysikey = service.gkey
                        dargs['service'] = 'j.atyourservice.getService(\'%s\')' % aysikey
                    kwargs.pop('service')
            else:
                raise j.exceptions.Input('service should be used as kwargs argument')
            
            state=service.state.getSet(self.name,default="INIT")

            if action:
                
                #this is safe for e.g.gevent usage, should always return recipe which is alike for all
                selfGeneratorCode="service=j.atyourservice.getService('%s');selfobj=service.actions" % aysikey

                action0 = j.actions.add(action=func, actionRecover=None, args=args, kwargs=kwargs, die=False, stdOutput=True,\
                    errorOutput=True, retry=0, executeNow=False, force=True, actionshow=actionshow,dynamicArguments=dargs,selfGeneratorCode=selfGeneratorCode)
                
                if service.hrd!=None:
                    action0.hrd=service.hrd
                action0._method=None
                action0.save()

                service.logger.info("Execute Action:%s %s"%(service,func.__name__ ))
                action0.execute()

                service.state.set(self.name,action0.state)
                service.save()                

                if not action0.state=="OK":
                    if die is False:
                        return action0
                    msg="**ERROR ACTION**:\n%s"%action0
                    # raise j.exceptions.RuntimeError()
                    service.logger.error (msg)
                    service.save()
                    sys.exit(1)

                return action0.result

            else:
                result = func(that, *args, **kwargs)

                #@todo escalation does not happen well
                # try:
                #     result = func(that, *args, **kwargs)
                # except Exception as e:
                #     service.state.set(func.__name__,"ERROR")
                #     if die:
                #         service.save()
                #         raise RuntimeError(e)
                #         sys.exit(1)
                #     else:
                #         return False

                service.state.set(func.__name__,"OK")

            service.save()

        functools.update_wrapper(wrapper, func)
        return wrapper
