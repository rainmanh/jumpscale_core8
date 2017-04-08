# Cuisine module

Here is an example cuisine module. Read the comments to see what is expected in the module.

```python
from JumpScale import j
from JumpScale.tools.cuisine.CuisineFactory import CuisineApp


class CuisineExample(CuisineApp):

    """
    always define the name of you module, it's used in
    the self.isInstalled method to check if your app is already present on the system
    """
    NAME = 'example'

    def _init(self):
        # if the module builds something, define BUILDDIR and CODEDIR folders.
        self.BUILDDIR = self.core.replace("$BUILDDIR/example/")
        self.CODEDIR = self.core.replace("$CODEDIR/github/example/myapp")

    def reset(self):
        """
        helper method to clean what this module generates.
        """
        super().reset()
        self.core.dir_remove(self.BUILDDIR)
        self.core.dir_remove(self.CODEDIR)
        self.cuisine.development.pip.reset()

    def _run(self, command):
        """
        to simplify your life, you can use this method to apply BUILDDIR and CODEDIR
        automatically during a 'run' command.

        this will let you do:
          self._run("cd $CODEDIR; make")

        and not:
          self.cuisine.core.run(self.replace("cd $CODEDIR; make"))
        """"
        return self.cuisine.core.run(self.replace(command))

    def build(self,  reset=False):
        """
        build method: it builds the application from source.
        This method downloads the source into the CODEDIR
        compile/build the code, the output of the building need to be in BUILDDIR

        Make sure your build supports all supported architecture. (linux, OSX, ...)

        if your app requires some dependencies, you can if the dependency is installed or not and try to installed it from here.
        The dependent cuisine module should have the isInstalled method to prevent installing twice the same app on the system.

        reset is a boolean used to reset before trying to build. If reset is true, we start clean and start the build from scratch
        """
        if reset is False and (self.isInstalled() or self.doneGet('build')):
            return

        self.cuisine.development.git.pullRepo("https://github.com/example/myapp")
        self.cuisine.core.run("cd $CODEDIR; ./configure --prefix=$BUILDDIR")
        self.cuisine.core.run("cd $CODEDIR; make")
        self.cuisine.core.run("cd $CODEDIR; make install")

        self.doneSet('build')

    def install(self, reset=False):
        """
        install method: copies the result of the build at the correct location in the jumpscale tree.
        use predefined folder: BINDIR, APPDIR, JSLIBDIR, JSAPPSDIR, ... for complete list check cuisine.core.dir_paths
        """
        # copy binaries, shared librairies, configuration templates,...
        self.cuisine.core.file_copy("$BUILDDIR/bin/myapp", '$BINDIR')

    def start(self, name):
        """
        start method: if you cuisine module is a starable application, the start method should start the app with some default configuration

        It can happens you app has two different star method. for example for a mongodb cuisine module, we could have
        a single instance start and a cluster start.

        Make sure to always specify a name/instance for the app, so we can start multiple time the same app on the system.
        for configuration use the $CFGDIR/myapp/name
        """
        self.cuisine.core.file_write('$TEMPLATEDIR/myapp/config', '$CFGDIR/myapp/name/config')
        self.cuisine.processmanager.ensure(name='myapp_' % name, cmd='$BINDIR/myapp --config $CFGDIR/myapp/name/config')

    def stop(self, name):
        """
        stop method, if you have a start method, you need a stop method wich stop the application stared with the start method.
        """
        self.cuisine.processmanager.stop(name='myapp_' % name)

    def getClient(self, name):
        """
        If your cuisine module is also a SAL over SSH, you can have some specific method discribed in it.
        """
        pass
```

```
!!!
title = "How To Write Cuisine Module"
date = "2017-04-08"
tags = ["howto"]
```
