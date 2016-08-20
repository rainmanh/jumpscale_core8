from JumpScale import j


from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.skydns"

base = j.tools.cuisine.getBaseClass()


class SkyDns(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    
    def build(self, start=True):
        self._cuisine.golang.install()
        self._cuisine.golang.get("github.com/skynetservices/skydns")
        self._cuisine.core.file_copy(self._cuisine.core.joinpaths('$goDir', 'bin', 'skydns'), '$binDir')
        self._cuisine.bash.addPath(self._cuisine.core.args_replace("$binDir"))

        if start:
            self.start()

    
    def start(self):
        cmd = self._cuisine.bash.cmdGetPath("skydns")
        self._cuisine.processmanager.ensure("skydns", cmd + " -addr 0.0.0.0:53")
