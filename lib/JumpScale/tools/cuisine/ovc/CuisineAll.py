from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineAll(app):
    def clean(self, root='/opt/jumpscale7'):
        self.cuisine.core.dir_remove(root)

    def build(self, root='/opt/jumpscale7', corebranch='master', ovcbranch='master'):
        self.cuisine.ovc.jumpscale.build(root, corebranch)
        self.cuisine.ovc.portal.build(root, corebranch)
