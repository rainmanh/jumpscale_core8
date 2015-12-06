from JumpScale import j
from .ExecutorBase import *


class ExecutorSSH(ExecutorBase):

    def __init__(self, addr, port, dest_prefixes={},login="root",passwd=None,debug=False,checkok=False,allow_agent=True, look_for_keys=True):
        ExecutorBase.__init__(self, dest_prefixes=dest_prefixes,debug=debug,checkok=checkok)
        self.addr = addr
        self.port = int(port)
        self.login=login
        self.passwd=passwd
        self.allow_agent=allow_agent
        self.look_for_keys=look_for_keys
        self._sshclient=None
        if checkok:
            self.sshclient.connectTest()


    @property
    def sshclient(self):
        if self._sshclient==None:
            self._sshclient=j.clients.ssh.get(self.addr,self.port,login=self.login,passwd=self.passwd,allow_agent=self.allow_agent, look_for_keys=self.look_for_keys)
        return self._sshclient

    def execute(self, cmds, die=True,checkok=None,showout=True):
        """
        @param naked means will not manipulate cmd's to show output in different way
        return (rc,out,err)
        """
        # print("cmds:%s"%cmds)
        cmds2=self._transformCmds(cmds,die,checkok=checkok)

        
        if cmds.find("\n") != -1:
            if showout:
                print("EXECUTESCRIPT} %s:%s:\n%s"%(self.addr,self.port,cmds))
            retcode,out=j.do.executeBashScript(content=cmds2,path=None,die=die,remote=self.addr,sshport=self.port)
        else:
            # online command, we use cuisine
            if showout:
                print("EXECUTE %s:%s: %s"%(self.addr,self.port,cmds))
            # return j.do.execute("ssh -A -p %s root@%s '%s'"%(self.port,self.addr,cmds),dieOnNonZeroExitCode=die)
            retcode,out=self.sshclient.execute(cmds2,die=die,showout=showout)

        if checkok and die:
            self.checkok(cmds,out)

        return (retcode,out)


    def upload(self, source, dest, dest_prefix="",recursive=True):

        if dest_prefix != "":
            dest = j.do.joinPaths(dest_prefix,dest)
        if dest[0] !="/":
            raise RuntimeError("need / in beginning of dest path")            
        dest = "root@%s:%s" % (self.addr, dest)
        j.do.copyTree(source, dest, keepsymlinks=True, deletefirst=False, \
            overwriteFiles=True, ignoredir=[".egg-info", ".dist-info"], ignorefiles=[".egg-info"], rsync=True,\
            ssh=True, sshport=self.port,recursive=recursive)


    def download(self, source, dest, source_prefix="",recursive=True):
        if source_prefix != "":
            source = j.do.joinPaths(source_prefix,source)
        if source[0] !="/":
            raise RuntimeError("need / in beginning of source path")        
        source = "root@%s:%s" % (self.addr,source)
        j.do.copyTree(source, dest, keepsymlinks=True, deletefirst=False, \
            overwriteFiles=True, ignoredir=[".egg-info",".dist-info"], ignorefiles=[".egg-info"], rsync=True,\
            ssh=True, sshport=self.port,recursive=recursive)

