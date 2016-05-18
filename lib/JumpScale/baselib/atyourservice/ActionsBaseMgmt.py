from JumpScale import j


class ActionsBaseMgmt:

    def change_hrd_template(self, service, originalhrd):
        for methodname,obj in service.state.methods.items():
            if methodname in ["install"]:
                service.state.set(methodname,"CHANGEDHRD")
                service.state.save()


    def change_hrd_instance(self, service, originalhrd):
        for methodname,obj in service.state.methods.items():
            if methodname in ["install"]:
                service.state.set(methodname,"CHANGEDHRD")
                service.state.save()

    def change_method(self, service, methodname):
        service.state.set(methodname, "CHANGED")
        service.state.save()

