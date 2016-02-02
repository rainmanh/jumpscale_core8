
from JumpScale import j

class ActionDecorator(object):

    def __init__(self,action=False,force=False):
        self.action=action
        self.force=force
    def __call__(self, func):

        def wrapper(*args, **kwargs):
            actionbase=self.action
            forcebase=self.force
            cm=self.selfobjCode
            cuisine=args[0].cuisine
            if "action" in kwargs:
                action=kwargs.pop("action")
            else:
                action=actionbase
            if "force" in kwargs:
                force=kwargs.pop("force")
            else:
                force=forcebase

            if action:
                args=args[1:]
                cm=cm.replace("$id",cuisine.id)  #replace the code which has the constructor code for the selfobj to work on
                j.actions.setRunId(cuisine.runid)
                action0=j.actions.add(action=func, actionRecover=None,args=args,kwargs=kwargs,die=True,stdOutput=True,errorOutput=True,retry=0,executeNow=True,selfGeneratorCode=cm,force=force)

                if action0.state!="OK":
                    if "die" in kwargs:
                        if kwargs["die"]==False:
                            return action0
                    raise RuntimeError("**ERROR**:\n%s"%action0)            
                return action0.result
            else:
                return func(*args,**kwargs)
        return wrapper
