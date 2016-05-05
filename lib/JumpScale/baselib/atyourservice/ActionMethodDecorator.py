
from JumpScale import j
import colored_traceback
colored_traceback.add_hook(always=True)
import functools
import sys

class ActionMethodDecorator(object):

    def __init__(self,action=True,force=False,actionshow=True,actionMethodName="",queue=""):
        self.action=action
        self.force=force
        self.actionshow=actionshow
        self.name=actionMethodName

    def __call__(self, func):

        def wrapper(*args, **kwargs):

            cm=self.selfobjCode

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
                args=args[1:]

                action0=j.actions.add(action=func, actionRecover=None,args=args,kwargs=kwargs,die=False,stdOutput=True,\
                    errorOutput=True,retry=0,executeNow=False,selfGeneratorCode=cm,force=True,actionshow=actionshow)

                service=action0.selfobj.service
                
                if force:
                    service.state.set(action0.name,"DO")

                stateitem=service.state.getObject(action0.name,default="AINIT")

                # method_hash=service.recipe.actionsmeta.methods[action0.name].hash
                # hrd_hash=service.hrdhash

                # if stateitem.hrd_hash!=hrd_hash:
                #     stateitem.state="CHANGEDHRD"                    
                #     service.save()
                #     service.actions.change(stateitem)

                # if stateitem.actionmethod_hash!=method_hash:
                #     stateitem.state="CHANGED"
                #     service.save()
                #     service.actions.change(stateitem)

                # if stateitem.name == 'init':
                #     stateitem.state = "CHANGED"

                if stateitem.state=="OK":
                    service.logger.info ("NOTHING TODO OK: %s"%stateitem)
                    action0.state="OK"
                    action0.save()
                    return action0.result

                if stateitem.state=="DISABLED":
                    service.logger.info ("NOTHING TODO DISABLED: %s"%stateitem)
                    action0.state="DISABLED"
                    action0.save()
                    return

                if func.__name__ not in ["init","input"]:
                    action0.hrd=service.hrd
                    action0._method=None
                    action0.save()


                service.logger.info("Execute Action:%s %s"%(service,func.__name__ ))
                action0.execute()
                    
                stateitem.state=action0.state

                stateitem.last=j.data.time.epoch
                
                if action0.state=="OK":
                    stateitem.hrd_hash=service.hrdhash
                    stateitem.actionmethod_hash=service.recipe.actionsmeta.methods[action0.name].hash
                else:
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
                return func(*args,**kwargs)

        functools.update_wrapper(wrapper, func)
        return wrapper
