from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineBrotli(app):

    NAME = 'bro'

    def build(self, reset=False):
        if reset is False and self.isInstalled():
            return
        sudo = 'sudo'
        if self._cuisine.core.isMac:
            sudo = ''
        C = """
        cd /tmp
        %s rm -rf brotli/
        git clone https://github.com/google/brotli.git
        cd /tmp/brotli/
        ./configure
        make bro
        """ % sudo
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.execute_bash(C)

    def install(self):
        C = """
        cp /tmp/brotli/bin/bro /usr/local/bin/
        rm -rf /tmp/brotli
        """
        self._cuisine.core.execute_bash(C)
        self._cuisine.development.pip.install('brotli>=0.5.2')
