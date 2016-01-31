
from JumpScale import j

#will be executed using actions
def actionrun(func):
    def wrapper(*args, **kwargs):
        cuisine=args[0].cuisine
        force=kwargs.pop("force",False)
        if j.tools.cuisine.useActions:
            args=args[1:]
            # result = func(*args, **kwargs)
            cm="cuisine=j.tools.cuisine.getFromId('%s');selfobj=cuisine.pip"%cuisine.id            
            j.actions.setRunId(cuisine.runid)
            # j.actions.run() #empty queue if still something there

            action=j.actions.add(action=func,actionRecover=None,args=args,kwargs=kwargs,die=True,stdOutput=True,errorOutput=True,retry=0,executeNow=True,selfGeneratorCode=cm,force=force)

            if action.state!="OK":
                if "die" in kwargs:
                    if kwargs["die"]==False:
                        return action
                raise RuntimeError("**ERROR**:\n%s"%action)            
            return action.result
        else:
            return func(*args,**kwargs)
    return wrapper

class CuisinePIP():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine


    # -----------------------------------------------------------------------------
    # PIP PYTHON PACKAGE MANAGER
    # -----------------------------------------------------------------------------

    @actionrun
    def upgrade(self,package):
        '''
        The "package" argument, defines the name of the package that will be upgraded.
        '''
        self.cuisine.run('pip3 install --upgrade %s' % (package))

    @actionrun
    def install(self,package=None,upgrade=False):
        '''
        The "package" argument, defines the name of the package that will be installed.
        '''
        cmd="pip3 install %s"%package
        if upgrade:
            cmd+=" --upgrade"
        self.cuisine.run(cmd)

    @actionrun
    def remove(self,package):
        '''
        The "package" argument, defines the name of the package that will be ensured.
        The argument "r" referes to the requirements file that will be used by pip and
        is equivalent to the "-r" parameter of pip.
        Either "package" or "r" needs to be provided
        '''
        return self.cuisine.run('pip3 uninstall %s' %(package))

    @actionrun
    def multiInstall(self,packagelist,upgrade=False):
        """
        @param packagelist is text file and each line is name of package
        can also be list @todo

        e.g.
            # influxdb
            # ipdb
            # ipython
            # ipython-genutils
            itsdangerous
            Jinja2
            # marisa-trie
            MarkupSafe
            mimeparse
            mongoengine

        @param runid, if specified actions will be used to execute
        """
        for dep in packagelist.split("\n"):
            dep=dep.strip()
            if dep.strip()=="":
                continue
            if dep.strip()[0]=="#":
                continue
            dep=dep.split("=",1)[0]
            self.install(dep,upgrade)



        

