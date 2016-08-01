from JumpScale import j
from ActionDecorator import ActionDecorator


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.lua"


base=j.tools.cuisine.getBaseClass()
class CuisineLua(base):

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine

    @actionrun(action=True)
    def install(self):
        """
        installs and builds geodns from github.com/abh/geodns
        """
        # deps
        self.cuisine.package.install("lua5.1",force=False)
        self.cuisine.package.install("luarocks",force=False)

        url="https://raw.githubusercontent.com/zserge/luash/master/sh.lua"
        #check http://zserge.com/blog/luash.html
        #curl -L https://github.com/luvit/lit/raw/master/get-lit.sh | sh
        #luasec
        #curl https://raw.githubusercontent.com/slembcke/debugger.lua/master/debugger.lua > /usr/local/share/lua/5.1/debugger.lua

        self.package("luasocket")

    @actionrun(action=True)
    def package(self,name):
        #@todo need to check for e.g. openwrt
        self.cuisine.core.run("luarocks install %s"%name)


    # local socket = require("socket")
