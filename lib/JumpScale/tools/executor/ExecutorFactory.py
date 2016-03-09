from JumpScale import j

from ExecutorSSH import *
from ExecutorLocal import *


class ExecutorFactory():

    def __init__(self):
        self.__jslocation__ = "j.tools.executor"
        self._executors = {}

    def pushkey(self, addr, passwd, keyname="",pubkey="", port=22, login="root"):
        """
        @param keyname is name of key (pub)
        @param pubkey is the content of the pub key
        """
        ExecutorSSH(addr, port=port, login=login, passwd=passwd, pushkey=keyname,pubkey=pubkey)

    def get(self, executor="localhost"):
        """
        @param executor is an executor object, None or $hostname:$port or $ipaddr:$port or $hostname or $ipaddr
        """
        #  test if it's in cache
        if executor in self._executors:
            return self._executors[executor]

        if executor in ["localhost", "", None, "127.0.0.1"]:
            if 'localhost' not in self._executors:
                local = self.getLocal()
                self._executors['localhost'] = local
            return self._executors['localhost']

        elif j.data.types.string.check(executor):
            if executor.find(":") > 0:
                # ssh with port
                addr, port = executor.split(":")
                return self.getSSHBased(addr=addr.strip(), port=int(port))
            else:
                return self.getSSHBased(addr=executor.strip())
        else:
            return executor

    def getLocal(self, jumpscale=False, debug=False, checkok=False):
        return ExecutorLocal(debug=debug, checkok=debug)

    def getSSHBased(self, addr="localhost", port=22, login="root", passwd=None, debug=False, checkok=True, allow_agent=True, look_for_keys=True, pushkey=None,pubkey=""):
        key = '%s:%s:%s' % (addr, port, login)
        h = j.data.hash.md5_string(key)
        if h not in self._executors:
            self._executors[h] = ExecutorSSH(addr, port=port, login=login, passwd=passwd, debug=debug, checkok=checkok, allow_agent=allow_agent, look_for_keys=look_for_keys, pushkey=pushkey,pubkey=pubkey)
        return self._executors[h]

    def getJSAgentBased(self, agentControllerClientKey, debug=False, checkok=False):
        return ExecutorAgent2(addr, debug=debug, checkok=debug)
