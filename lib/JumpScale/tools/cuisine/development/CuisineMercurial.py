
from JumpScale import j


base = j.tools.cuisine._getBaseClass()


class CuisineMercurial(base):

    def install(self):
        C = """
        mercurial
        """
        self.cuisine.package.multiInstall(C)

    def pullRepo(self, url, dest=None,
                 ignorelocalchanges=True, reset=False, branch=None, timeout=1200):

        if not self.cuisine.core.command_check("hg"):
            self.install()

        name = j.sal.fs.getBaseName(url)

        if dest == None:
            dest = "$CODEDIR/mercurial/%s" % name

        dest = self.replace(dest)

        if reset:
            self.cuisine.core.run("rm -rf %s" % dest)

        pdir = j.sal.fs.getParent(dest)

        self.log("mercurial pull %s" % (url))

        if self.cuisine.core.dir_exists(dest):
            cmd = "set -ex; cd %s;hg pull %s" % (dest, url)
        else:
            cmd = "set -ex;mkdir -p %s; cd %s;hg clone %s" % (pdir, pdir, url)

        rc, out, err = self.cuisine.core.run(cmd)

        return (dest)
