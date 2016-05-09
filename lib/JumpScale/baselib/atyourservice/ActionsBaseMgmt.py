from JumpScale import j


class ActionsBaseMgmt():
    def __init__(self, role, instance, repopath, reponame):
        self.params = {'role': role, 'instance': instance, 'repopath': repopath, 'reponame': reponame}
        self.aysrepo = j.atyourservice.get(reponame, repopath)
        self._service = None

    @property
    def service(self):
        if not self._service:
            self._service = self.aysrepo.getService(self.params['role'], self.params['instance'])
        return self._service

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
