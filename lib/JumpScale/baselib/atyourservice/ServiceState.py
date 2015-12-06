from JumpScale import j


def log(msg, level=1):
    j.logger.log(msg, level=level, category='JSERVICE')


class ServiceState():
    def __init__(self, service):

        self.service = service

        if self.service.path == "" or self.service.path is None:
            raise RuntimeError("path cannot be empty")

        self.path = j.sal.fs.joinPaths(self.service.path, "state.hrd")
        if not j.sal.fs.exists(self.path):
            self.hrd = j.data.hrd.get(self.path)
            items = ["action_mgmt", "action_node", "action_tmpl"]
            for item in items:
                self.hrd.set("hash.%s.py" % item, "")
            self.hrd.set("hash.recipe.hrd", "")
            self.hrd.set("hash.instance.hrd", "")
            self.hrd.set("hash.template.hrd", "")
            self.hrd.set("hrd.instance.changed", True)
            self.hrd.set("hrd.template.changed", True)
            self.hrd.set("actions.changed", True)
            self.hrd.set("disabled", False)
        else:
            self.hrd = j.data.hrd.get(self.path)

    def check(self):
        if self._checkActionsChangeState():
            return True
        if self._checkHRDChangeState():
            return True
        return False

    def _checkHRDChangeState(self):
        (self._checkTemplateHRDChangeState() or self._checkInstanceHRDChangeState())

    def _checkTemplateHRDChangeState(self):
        if j.tools.hash.md5(j.sal.fs.joinPaths(self.service.path, 'template.hrd')) != self.hrd.get("hash.template.hrd"):
            return True
        return False

    def _checkInstanceHRDChangeState(self):
        if j.tools.hash.md5(j.sal.fs.joinPaths(self.service.path, 'instance.hrd')) != self.hrd.get("hash.instance.hrd"):
            return True
        return False

    def _checkActionsChangeState(self):
        items = ["action_mgmt", "action_node", "action_tmpl"]
        for item in items:
            source = "%s/%s.py" % (self.service.path, item)
            if j.sal.fs.exists(source):
                if j.tools.hash.md5(j.sal.fs.joinPaths(self.service.path, '%s.py' % item)) != self.hrd.get("hash.%s.py" % item):
                    return True
        return False

    @property
    def changed(self):
        if self.hrd.getBool("actions.changed") or \
           self.hrd.getBool("hrd.instance.changed") or \
           self.hrd.getBool("hrd.template.changed"):
            return True
        return False

    def saveState(self):
        if self._checkActionsChangeState():
            self.hrd.set("actions.changed", True)
        if self._checkInstanceHRDChangeState():
            self.hrd.set("hrd.instance.changed", True)
        if self._checkTemplateHRDChangeState():
            self.hrd.set("hrd.template.changed", True)

        items = ["action_mgmt", "action_node", "action_tmpl"]
        for item in items:
            action_path = "%s.py" % item
            if j.sal.fs.exists(path=action_path):
                self.hrd.set("hash.%s.py" % item, j.tools.hash.md5(j.sal.fs.joinPaths(self.service.path, action_path)))
        self.hrd.set("hash.template.hrd", j.tools.hash.md5(j.sal.fs.joinPaths(self.service.path, 'template.hrd')))
        self.hrd.set("hash.instance.hrd", j.tools.hash.md5(j.sal.fs.joinPaths(self.service.path, 'instance.hrd')))

    def commitHRDChange(self, oldHRD, newHRD):
        change = []
        for key, val in newHRD.items.items():
            if key not in oldHRD.items:
                change.append({
                     "type": "N",
                     "name": key,
                     "prev": "",
                     "new": val.data})
            elif str(oldHRD.items[key].data) != str(val.data):
                change.append({
                    "type": "M",
                    "name": key,
                    "prev": oldHRD.items[key].data,
                    "new": val.data})
        for key, val in oldHRD.items.items():
            if key not in newHRD.items:
                change.append({
                    "type": "D",
                    "name": key,
                    "prev": oldHRD.items[key].data,
                    "new": ""})

        for item in change:
            name = item["name"]
            self.hrd.set("hrd.changes.%s" % name, item["type"])

    def installDoneOK(self):
        for key in self.hrd.prefix("hrd.changes"):
            self.hrd.delete(key)
        self.hrd.set("actions.changed", False)
        self.saveState()
        self.hrd.set("hrd.instance.changed", False)
        self.hrd.set("hrd.template.changed", False)
        self.hrd.set("actions.changed", False)

    def __repr__(self):
        return str(self.hrd)

    def __str__(self):
        return self.__repr__()
