from JumpScale import j


def log(msg, level=1):
    j.logger.log(msg, level=level, category='AYS_STATE')


from ServiceRecipeState import ServiceRecipeState

class ServiceState(ServiceRecipeState):
    def __init__(self, service):

        self.service = service
        self._recipeOrService=service
        if self.service.path == "" or self.service.path is None:
            raise RuntimeError("path cannot be empty")

        self.path = j.sal.fs.joinPaths(self.service.path, "state.hrd")
        if not j.sal.fs.exists(self.path):
            self.hrd = j.data.hrd.get(self.path)
            self.hrd.set("hash.instance.hrd", "")
            self.hrd.set("ischanged.instance.hrd", False)

            self.hrd.set("disabled", False)
        else:
            self.hrd = j.data.hrd.get(self.path)


    def __repr__(self):
        return str(self.hrd)

    def __str__(self):
        return self.__repr__()
