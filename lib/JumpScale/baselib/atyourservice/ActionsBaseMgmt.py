from JumpScale import j


class ActionsBaseMgmt():

    def change_hrd_template(self,originalhrd):
        for methodname,obj in self.service.state.methods.items():
            if methodname in ["install"]:
                self.service.state.set(methodname,"CHANGEDHRD")


    def change_hrd_instance(self,originalhrd):
        for methodname,obj in self.service.state.methods.items():
            if methodname in ["install"]:
                self.service.state.set(methodname,"CHANGEDHRD")
        
    def change_method(self,methodname):
        self.service.state.set(methodname,"CHANGE")
