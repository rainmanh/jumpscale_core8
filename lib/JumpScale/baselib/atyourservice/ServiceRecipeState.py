from JumpScale import j


def log(msg, level=1):
    j.logger.log(msg, level=level, category='AYS_SCHEMA')


class ServiceRecipeState():
    def __init__(self, recipe):

        self.recipe = recipe
        self._recipeOrService=recipe

        self.path = j.sal.fs.joinPaths(self.recipe.path, "state.hrd")

        if not j.sal.fs.exists(self.path):
            self.hrd = j.data.hrd.get(self.path)
            items = ["action_mgmt", "action_node"]
            for item in items:
                self.hrd.set("hash.%s.py" % item, "")
                self.hrd.set("ischanged.%s.py"%item, False)
            self.hrd.set("hash.service.hrd", "")
            self.hrd.set("ischanged.service.hrd", False)
            self.hrd.set("hash.schema.hrd", "")
            self.hrd.set("ischanged.schema.hrd", False)

            self.hrd.set("disabled", False)
            self.hrd.set("template.name",self.recipe.parent.name)
            self.hrd.set("template.domain",self.recipe.parent.domain)
            self.hrd.set("template.version",self.recipe.parent.version) 
        else:
            self.hrd = j.data.hrd.get(self.path)

    def check(self):
        for item in self.hrd.prefix("hash."):
            #lists the different has entries
            item2=item.replace("hash.","")
            path=j.do.joinPaths(self._recipeOrService.path,item2)
            if j.do.exists(path):
                md5=j.tools.hash.md5(path)
                if md5!=self.hrd.get(item,md5):
                    self.hrd.set("ischanged.%s"%item2,True)
        return False


    @property
    def changed(self):
        for item in self.hrd.prefix("ischanged."):
            if self.hrd.getBool(item)==True:
                return True
        return False

    def save(self):
        for item in self.hrd.prefix("hash."):
            #lists the different has entries
            item2=item.replace("hash.","")
            path=j.do.joinPaths(self._recipeOrService.path,item2)
            if j.do.exists(path):
                md5=j.tools.hash.md5(path)
                self.hrd.set(item,md5)

    def reset(self):
        for key in self.hrd.prefix("hrd.changes"):
            self.hrd.delete(key)
        for item in self.hrd.prefix("ischanged."):
            self.hrd.set(item,False)
        for item in self.hrd.prefix("hash."):
            self.hrd.set(item,"")
        self.saveState()


    # def commitHRDChange(self, oldHRD, newHRD):
    #     change = []
    #     for key, val in newHRD.items.items():
    #         if key not in oldHRD.items:
    #             change.append({
    #                  "type": "N",
    #                  "name": key,
    #                  "prev": "",
    #                  "new": val.data})
    #         elif str(oldHRD.items[key].data) != str(val.data):
    #             change.append({
    #                 "type": "M",
    #                 "name": key,
    #                 "prev": oldHRD.items[key].data,
    #                 "new": val.data})
    #     for key, val in oldHRD.items.items():
    #         if key not in newHRD.items:
    #             change.append({
    #                 "type": "D",
    #                 "name": key,
    #                 "prev": oldHRD.items[key].data,
    #                 "new": ""})

    #     for item in change:
    #         name = item["name"]
    #         self.hrd.set("hrd.changes.%s" % name, item["type"])                

    def __repr__(self):
        return str(self.hrd)

    def __str__(self):
        return self.__repr__()
