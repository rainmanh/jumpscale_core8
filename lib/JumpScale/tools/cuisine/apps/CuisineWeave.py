from JumpScale import j


from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.weave"

base = j.tools.cuisine.getBaseClass()


class Weave(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    
    def install(self, start=True, peer=None, jumpscalePath=True):
        if jumpscalePath:
            binPath = self._cuisine.core.joinpaths(
                self._cuisine.core.dir_paths['binDir'], 'weave')
        else:
            binPath = '/usr/local/bin/weave'
        self._cuisine.core.dir_ensure(j.sal.fs.getParent(binPath))

        C = '''
        curl -L git.io/weave -o {binPath} && sudo chmod a+x {binPath}
        '''.format(binPath=binPath)
        C = self._cuisine.core.args_replace(C)
        self._cuisine.docker.install()
        self._cuisine.package.ensure('curl')
        self._cuisine.core.run_script(C, profile=True)
        self._cuisine.bash.addPath(j.sal.fs.getParent(binPath))
        if start:
            self.start(peer)

    
    def start(self, peer=None):
        rc, out, err = self._cuisine.core.run("weave status", profile=True, die=False, showout=False)
        if rc != 0:
            cmd = 'weave launch'
            if peer:
                cmd += ' %s' % peer
            self._cuisine.core.run(cmd, profile=True)

        _, env, _ = self._cuisine.core.run('weave env', profile=True)
        ss = env[len('export'):].strip().split(' ')
        for entry in ss:
            splitted = entry.split('=')
            if len(splitted) == 2:
                self._cuisine.bash.environSet(splitted[0], splitted[1])
            elif len(splitted) > 0:
                self._cuisine.bash.environSet(splitted[0], '')
