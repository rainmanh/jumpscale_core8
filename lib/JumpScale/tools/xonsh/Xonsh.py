from JumpScale import j

try:
    import xonsh
except:
    j.do.executeInteractive("pip3 install colored-traceback")
    j.do.executeInteractive("pip3 install xonsh")
    j.do.executeInteractive("pip3 install pudb")
    j.do.executeInteractive("pip3 install tmuxp")
    import xonsh


#from pudb import set_trace; set_trace()    


class Xonsh:
    def __init__(self):
        self.__jslocation__ = "j.tools.xonsh"
        self.executor=j.tools.executor.getLocal()
        self.cuisine=self.executor.cuisine
        

    def configAll(self):
        self.config()
        self.configTmux(True)

    def config(self):
        C="""
        from JumpScale import j
        $XONSH_SHOW_TRACEBACK = True
        $XONSH_STORE_STDOUT = True
        $XONSH_LOGIN = True

        #from pprint import pprint as print

        import colored_traceback
        colored_traceback.add_hook(always=True)
        import sys


        from tools.xonsh.XonshAliases import *

        aliases['jsgo'] = xonsh_go
        aliases['jsedit'] = xonsh_edit
        aliases['jsupdate'] = xonsh_update


        """
        self.cuisine.file_write("$homeDir/.xonshrc",C)


    def configTmux(self,restart=True):
        self.cuisine.tmux.configure(restart,True)





