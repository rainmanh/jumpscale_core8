from JumpScale import j

base = j.tools.cuisine._getBaseClassLoader()


class ovc(base):

    def __init__(self, executor, cuisine):
        base.__init__(self, executor, cuisine)
