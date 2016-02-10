
from CuisineProcessManager import CuisineRunit, CuisineTmuxec, CuisineSystemd
from JumpScale import j

class ProcessManagerFactory:

    pms = {}

    @classmethod
    def systemdOK(cls, cuisine):
        return not cuisine.isDocker and cuisine.command_check("systemctl")

    @classmethod
    def svOK(cls, cuisine):
        return cuisine.command_check("sv")

    @classmethod
    def get_prefered(cls, cuisine):
        for pm in ["systemd", "sv", "tmux"]:
            if cls.is_available(cuisine, pm):
                return pm
    
    @classmethod
    def is_available(cls, cuisine, pm):
        if pm == "systemd":
            return cls.systemdOK(cuisine)
        elif pm == "sv":
            return cls.svOK(cuisine)
        elif pm == "tmux":
            return True
        else:
            return False

    @classmethod
    def get(cls, cuisine, pm = None):
        if pm == None:
            pm = cls.get_prefered(cuisine)
        else:
            if not cls.is_available(cuisine, pm):
                return j.errorconditionhandler.raiseCritical('%s processmanager is not available on your system'%(pm))

        if pm not in cls.pms:
            if pm == "systemd":
                inst = CuisineSystemd(cuisine.executor, cuisine)
            elif pm == "sv":
                inst = CuisineRunit(cuisine.executor, cuisine)
            elif pm == "tmux":
                inst = CuisineTmuxec(cuisine.executor, cuisine)
            cls.pms[pm] = inst

        return cls.pms[pm]
