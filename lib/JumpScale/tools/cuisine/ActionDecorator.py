
from JumpScale import j
import colored_traceback
colored_traceback.add_hook(always=True)
import functools
import sys

class ActionDecorator(object):

    def __init__(self,action=True,force=False,actionshow=True):
        self.action=action
        self.force=force
        self.actionshow=actionshow

    def __call__(self, func):

        def wrapper(*args, **kwargs):

            cm=self.selfobjCode
            cuisine=args[0].cuisine

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


            #action=False
            # force=True

            if action:
                args=args[1:]
                cm=cm.replace("$id",cuisine.id)  #replace the code which has the constructor code for the selfobj to work on
                j.actions.setRunId(cuisine.runid)
                action0=j.actions.add(action=func, actionRecover=None,args=args,kwargs=kwargs,die=False,stdOutput=True,\
                    errorOutput=True,retry=0,executeNow=True,selfGeneratorCode=cm,force=force,actionshow=actionshow)

                # from pudb import set_trace; set_trace() 
                

                if action0.state!="OK":
                    if "die" in kwargs:
                        if kwargs["die"]==False:
                            return action0
                    msg="**ERROR ACTION**:\n%s"%action0
                    # raise RuntimeError()
                    print (msg)
                    sys.exit(1)
                return action0.result
            else:
                return func(*args,**kwargs)
        functools.update_wrapper(wrapper, func)
        return wrapper
