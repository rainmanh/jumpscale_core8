from JumpScale import j

class HelloTool(object):

    def __init__(self):
        self.__jslocation__ = 'j.tools.hello'

    @staticmethod
    def new(msg='Hello'):
        return Hello(msg)

class Hello(object):

    def __init__(self, msg):
        self.msg=msg

    def upper(self):
        return self.msg.upper()

    def lower(self):
        return self.msg.lower()

    def manytimes(self, n):
        return (self.msg + " ")*n + "!!!"


    def morning(self):
        return 'morning'
