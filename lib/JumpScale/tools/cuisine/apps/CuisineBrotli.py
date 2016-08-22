from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()

class CuisineBrotli(app):

    NAME = 'bro'

    def build(self, reset=False):
        if reset == False and self.isInstalled():
            return
        C = """
        cd /tmp
        sudo rm -rf brotli/
        git clone https://github.com/google/brotli.git
        cd /tmp/brotli/
        ./configure
        make bro
        cp /tmp/brotli/bin/bro /usr/local/bin/
        rm -rf /tmp/brotli
        """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.run_script(C)
