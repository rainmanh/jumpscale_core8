from JumpScale import j


base = j.tools.cuisine._getBaseClass()


class CuisineBrotli(base):

    def isInstalled(self, die=False):
        rc1, out1, err = self._cuisine.core.run('which bro', die=False)
        if (rc1 == 0 and out1):
            return True
        return False

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
