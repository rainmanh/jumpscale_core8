from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisineZerotier(base):

    def _init(self):
        self.BUILDDIRL = self.core.replace("$BUILDDIR/zerotier/")

    def reset(self):
        self.core.dir_remove(self.BUILDDIRL)

    def build(self, reset=False, install=True):
        """
        """

        if reset:
            self.reset()

        if self.doneGet("build") and not reset:
            return

        if self.cuisine.core.isMac:
            if not self.doneGet("xcode_install"):
                self.cuisine.core.run("xcode-select --install", die=False, showout=True)
                self.doneSet("xcode_install")
        elif self.cuisine.core.isUbuntu:
            self.cuisine.package.ensure("gcc")
            self.cuisine.package.ensure("g++")
            self.cuisine.package.ensure('make')
        self.cuisine.package.ensure('npm')

        self.cuisine.development.git.pullRepo("https://github.com/zerotier/ZeroTierOne", dest=self.BUILDDIRL, reset=reset, depth=1, branch='master')

        C = """cd $BUILDDIRL && make"""
        C = C.replace('$BUILDDIRL', self.BUILDDIRL)
        self.cuisine.core.run(C, profile=True)

        self.doneSet("build")
        if install:
            self.install()

    def install(self):
        built = [item for item in self.cuisine.core.run("ls %s/" % self.BUILDDIRL)[1].split("\n") if item.startswith("zerotier-")]
        for item in built:
            self.cuisine.core.file_copy("%s/%s" % (self.BUILDDIRL, item), self.cuisine.core.dir_paths['BINDIR'])

    def start(self):
        self.cuisine.bash.profileDefault.addPath(self.cuisine.core.replace("$BINDIR"))
        self.cuisine.bash.profileDefault.save()
        self.cuisine.processmanager.ensure('zerotier-one', 'zerotier-one')

    def stop(self):
        self.cuisine.processmanager.stop('zerotier-one')
