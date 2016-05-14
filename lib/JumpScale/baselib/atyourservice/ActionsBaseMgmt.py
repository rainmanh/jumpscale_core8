from JumpScale import j


class ActionsBaseMgmt():

    # def __init__(self, role="", instance="", repopath="", reponame=""):
    #     self.params = {'role': role, 'instance': instance, 'repopath': repopath, 'reponame': reponame}
    #     self.aysrepo = j.atyourservice.get(reponame, repopath)
    #     self._service = None

    # @property
    # def service(self):
    #     if not self._service:
    #         self._service = self.aysrepo.getService(self.params['role'], self.params['instance'])
    #     return self._service

    def change_hrd_template(self,service,originalhrd):
        for methodname,obj in service.state.methods.items():
            if methodname in ["install"]:
                service.state.set(methodname,"CHANGEDHRD")
                service.state.save()


    def change_hrd_instance(self,service,originalhrd):
        for methodname,obj in service.state.methods.items():
            if methodname in ["install"]:
                service.state.set(methodname,"CHANGEDHRD")
                service.state.save()

    def change_method(self,service,methodname):
        service.state.set(methodname,"CHANGED")
        service.state.save()
