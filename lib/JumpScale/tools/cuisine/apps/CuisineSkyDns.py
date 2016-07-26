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

base=j.tools.cuisine.getBaseClass()
class SkyDns(base):

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine

    @actionrun(action=True)
    def build(self, start=True):
        self.cuisine.golang.install()
        self.cuisine.golang.get("github.com/skynetservices/skydns",action=True)
        self.cuisine.core.file_copy(self.cuisine.core.joinpaths('$goDir', 'bin', 'skydns'), '$binDir', action=True)
        self.cuisine.bash.addPath(self.cuisine.core.args_replace("$binDir"), action=True)

        if start:
            self.start()

    @actionrun(force=True)
    def start(self):
        cmd = self.cuisine.bash.cmdGetPath("skydns")
        self.cuisine.processmanager.ensure("skydns", cmd + " -addr 0.0.0.0:53")
