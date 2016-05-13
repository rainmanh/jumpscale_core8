from JumpScale import j


class ActionsBaseMgmt():
    def __init__(self, service):
        self.service = service


    def change_hrd_template(self,originalhrd):
        for methodname,obj in self.service.state.methods.items():
            if methodname in ["install"]:
                self.service.state.set(methodname,"CHANGEDHRD")


    def change_hrd_instance(self,originalhrd):
        for methodname,obj in self.service.state.methods.items():
            if methodname in ["install"]:
                self.service.state.set(methodname,"CHANGEDHRD")

    def change_method(self,methodname):
        self.service.state.set(methodname,"CHANGED")
