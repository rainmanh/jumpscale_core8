from JumpScale import j

import tmuxp

class Tmux():

    def __init__(self):
        self.__jslocation__ = "j.sal.tmux"

    def getServer(self):
        return tmuxp.Server()

    




