
from JumpScale import j
import colored_traceback
colored_traceback.add_hook(always=True)
import functools
import sys

class ActionMethodDecorator(object):

    def __init__(self,action=True,force=True,actionshow=True,actionMethodName="",queue=""):
        self.action=action
        self.force=force
        self.actionshow=actionshow
        self.name=actionMethodName

    def __call__(self, func):

        def wrapper(that, *args, **kwargs):
            cm=self.selfobjCode % that.params

            #args[0] is self
            # cuisine=args[0].cuisine

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
                force=kwargs.pop("force")
            else:
                force=self.force

            # print ("ACTION:START: isaction=%s"%action)
            # print(func)
            # if "getIssuesFromGithub" in str(func):
            #     from pudb import set_trace; set_trace() 

            if action:
                action0=j.actions.add(action=func, actionRecover=None,args=args,kwargs=kwargs,die=False,stdOutput=True,\
                    errorOutput=True,retry=0,executeNow=False,selfGeneratorCode=cm,force=True,actionshow=actionshow)

                service=action0.selfobj.service
                
                if force:
                    service.state.set(action0.name,"DO")

                state=service.state.getSet(action0.name,default="INIT")

                if state=="OK":
                    service.logger.info ("NOTHING TODO OK: %s"%action0.name)
                    action0.state="OK"
                    action0.save()
                    return action0.result

                if state=="DISABLED":
                    service.logger.info ("NOTHING TODO DISABLED: %s"%action0.name)
                    action0.state="DISABLED"
                    action0.save()
                    return

                if func.__name__ not in ["init","input"]:
                    if service.hrd!=None:
                        action0.hrd=service.hrd
                    action0._method=None
                    action0.save()

                service.logger.info("Execute Action:%s %s"%(service,func.__name__ ))
                action0.execute()
                    
                service.state.set(action0.name,action0.state)
                
                if not action0.state=="OK":
                    if "die" in kwargs:
                        if kwargs["die"]==False:
                            return action0
                    msg="**ERROR ACTION**:\n%s"%action0
                    # raise j.exceptions.RuntimeError()
                    service.logger.error (msg)
                    service.save()
                    sys.exit(1)

                service.save()                

                return action0.result
            else:
                return func(that, *args,**kwargs)

        functools.update_wrapper(wrapper, func)
        return wrapper
