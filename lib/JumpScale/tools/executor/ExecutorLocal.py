from JumpScale import j
from ExecutorBase import ExecutorBase
import subprocess
import os


class ExecutorLocal(ExecutorBase):

    def __init__(self, debug=False, checkok=False):
        ExecutorBase.__init__(self,  debug=debug, checkok=debug)

        self.type = "local"
        self._id = 'localhost'
        self._logger = None

    @property
    def logger(self):
        if self._logger == None:
            self._logger = j.logger.get("executor.localhost")
        return self._logger

    def executeRaw(self, cmd, die=True, showout=False):
        return self.execute(cmd, die=die, showout=showout)

    def execute(self, cmds, die=True, checkok=None, showout=True, outputStderr=None, timeout=600, env={}):
        if env:
            self.env.update(env)
        if self.debug:
            print("EXECUTOR:%s" % cmds)

        if outputStderr == None:
            outputStderr = showout

        if checkok == None:
            checkok = self.checkok

        cmds2 = self._transformCmds(cmds, die=die, checkok=checkok, env=env)

        rc, out, err = j.do.execute(cmds2, die=die,  showout=showout, outputStderr=outputStderr, timeout=timeout)

        if checkok:
            out = self.docheckok(cmds, out)

        return rc, out, err

    def executeInteractive(self, cmds, die=True, checkok=None):
        cmds = self._transformCmds(cmds, die, checkok=checkok)
        return j.sal.process.executeWithoutPipe(cmds)

    def upload(self, source, dest, dest_prefix="", recursive=True):
        if dest_prefix != "":
            dest = j.sal.fs.joinPaths(dest_prefix, dest)
        if j.sal.fs.isDir(source):
            j.sal.fs.copyDirTree(source, dest, keepsymlinks=True, deletefirst=False,
                                 overwriteFiles=True, ignoredir=[".egg-info", ".dist-info"], ignorefiles=[".egg-info"], rsync=True,
                                 ssh=False, recursive=recursive)
        else:
            j.sal.fs.copyFile(source, dest, overwriteFile=True)

    def download(self, source, dest, source_prefix=""):
        if source_prefix != "":
            source = j.sal.fs.joinPaths(source_prefix, source)
        j.sal.fs.copyDirTree(source, dest, keepsymlinks=True, deletefirst=False,
                             overwriteFiles=True, ignoredir=[".egg-info", ".dist-info"], ignorefiles=[".egg-info"], rsync=True,
                             ssh=False)
