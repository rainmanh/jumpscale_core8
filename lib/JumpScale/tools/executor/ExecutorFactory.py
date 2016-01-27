from JumpScale import j

from ExecutorSSH import *
from ExecutorLocal import *
# from ExecutorAgent2 import *

class ExecutorFactory():

    def __init__(self):
        self.__jslocation__ = "j.tools.executor"


    def pushkey(self,addr,passwd,keyname,port=22,login="root"):
        ExecutorSSH(addr,port=port,login=login ,passwd=passwd,pushkey=keyname)



    def get(self,executor="localhost"):
        """
        @param executor is an executor object, None or $hostname:$port or $ipaddr:$port or $hostname or $ipaddr
        """
        if executor in ["localhost","",None,"127.0.0.1"]:
            return self.getLocal()

        elif j.data.types.string.check(executor):
            if executor.find(":")>0:
                #ssh with port
                addr,port=executor.split(":")
                return self.getSSHBased(addr=addr.strip(),port=int(port))
            else:
                return self.getSSHBased(addr=executor.strip())
        else:
            return executor

    def getLocal(self,jumpscale=False,debug=False,checkok=False):
        return ExecutorLocal(debug=debug,checkok=debug)

    def getSSHBased(self,addr="localhost",port=22,login="root",passwd=None,debug=False,checkok=True,allow_agent=True, look_for_keys=True,pushkey=None):
        return ExecutorSSH(addr,port=port,login=login,passwd=passwd,debug=debug,checkok=checkok,allow_agent=allow_agent, look_for_keys=look_for_keys,pushkey=pushkey)

    def getJSAgent2Based(self,agentControllerClientKey,debug=False,checkok=False):
        return ExecutorAgent2(addr,debug=debug,checkok=debug)
