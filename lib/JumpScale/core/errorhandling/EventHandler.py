from JumpScale import j


class EventHandler:

    def __init__(self):
        self.__jslocation__ = "j.events"

    def bug_critical(self, msg, source=""):
        """
        will die
        @param e is python error object when doing except
        """
        print("change your code to no longer use j.events...., but raise j.exceptions...")
        raise j.exceptions.JSBUG(msg, source=source)

    def opserror_critical(self, msg):
        """
        will die
        """
        print("change your code to no longer use j.events...., but raise j.exceptions...")
        raise j.exceptions.OPERATIONS(msg)

    def opserror_warning(self, msg, category=""):
        """
        will NOT die
        """
        j.errorconditionhandler.raiseWarning(
            message=msg, msgpub=msgpub, tags='category:%s' % category, level=level)

    def inputerror_critical(self, msg, category="", msgpub=""):
        """
        will die
        """
        print("change your code to no longer use j.events...., but raise j.exceptions...")
        raise j.exceptions.Input(msg, tags='category:%s' %
                                 category, msgpub=msgpub)

    def inputerror_warning(self, msg, category="", msgpub="", level=5):
        """
        """
        j.errorconditionhandler.raiseWarning(
            message=msg, msgpub=msgpub, tags='category:%s' % category, level=level)
