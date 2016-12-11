
from JumpScale import j


base = j.tools.cuisine._getBaseClass()


class CuisineMercurial(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def install(self):
        C = """
        mercurial
        """
        self._cuisine.package.multiInstall(C)

    def pullRepo(self, url, dest=None,
                 ignorelocalchanges=True, reset=False, branch=None):

        if not self._cuisine.core.command_check("hg"):
            self.install()

        name = j.sal.fs.getBaseName(url)

        if dest == None:
            dest = "$codeDir/mercurial/%s" % name

        dest = self._cuisine.core.args_replace(dest)

        if reset:
            self._cuisine.core.run("rm -rf %s" % dest)

        pdir = j.sal.fs.getParent(dest)

        print("mercurial pull %s" % (url))

        if self._cuisine.core.dir_exists(dest):
            cmd = "set -ex; cd %s;hg pull %s" % (dest, url)
        else:
            cmd = "set -ex;mkdir -p %s; cd %s;hg clone %s" % (pdir, pdir, url)

        rc, out, err = self._cuisine.core.run(cmd)

        return (dest)
