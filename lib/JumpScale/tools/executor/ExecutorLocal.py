from JumpScale import j
from .ExecutorBase import ExecutorBase


class ExecutorLocal(ExecutorBase):

    def __init__(self, dest_prefixes={}, debug=False, checkok=False):
        ExecutorBase.__init__(
            self, dest_prefixes=dest_prefixes, debug=debug, checkok=debug)

    def execute(self, cmds, die=True, checkok=None, async=False):
        cmds = self._transformCmds(cmds, die, checkok=checkok)
        if cmds.find('\n') == -1:
            return j.do.execute(cmds, dieOnNonZeroExitCode=die, async=async)
        return j.do.executeBashScript(content=cmds, path=None, die=die)

    def executeInteractive(self, cmds, die=True, checkok=None):
        cmds = self._transformCmds(cmds, die, checkok=checkok)
        return j.do.executeInteractive(cmds)

    def upload(self, source, dest, dest_prefix="", recursive=True):
        if dest_prefix != "":
            dest = j.do.joinPaths(dest_prefix, dest)
        j.do.copyTree(source, dest, keepsymlinks=True, deletefirst=False,
                      overwriteFiles=True, ignoredir=[".egg-info", ".dist-info"], ignorefiles=[".egg-info"], rsync=True,
                      ssh=False, recursive=recursive)

    def download(self, source, dest, source_prefix=""):
        if source_prefix != "":
            source = j.do.joinPaths(source_prefix, source)
        j.do.copyTree(source, dest, keepsymlinks=True, deletefirst=False,
                      overwriteFiles=True, ignoredir=[".egg-info", ".dist-info"], ignorefiles=[".egg-info"], rsync=True,
                      ssh=False)
