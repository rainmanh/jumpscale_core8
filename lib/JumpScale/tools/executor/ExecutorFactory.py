from JumpScale import j

from ExecutorSSH import *
from ExecutorLocal import *
# from ExecutorAgent2 import *

class ExecutorFactory():

    def __init__(self):
        self.__jslocation__ = "j.tools.executor"

    def getLocal(self,jumpscale=True,debug=False,checkok=False):
        return ExecutorLocal(debug=debug,checkok=debug)

    def getSSHBased(self,addr="localhost",port=22,login="root",passwd=None,debug=False,checkok=False,allow_agent=True, look_for_keys=True):
        return ExecutorSSH(addr,port=port,login=login,passwd=passwd,debug=debug,checkok=debug,allow_agent=allow_agent, look_for_keys=look_for_keys)

    def getJSAgent2Based(self,agentControllerClientKey,debug=False,checkok=False):
        return ExecutorAgent2(addr,debug=debug,checkok=debug)
