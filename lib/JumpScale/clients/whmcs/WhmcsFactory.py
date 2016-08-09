from JumpScale import j
from JumpScale.clients.whmcs.WhmcsInstance import WhmcsInstance


class Dummy:

    def __getattribute__(self, attr, *args, **kwargs):
        def dummyFunction(*args, **kwargs):
            pass
        return dummyFunction

    def __setattribute__(self, attr, val):
        pass


class DummyWhmcs:

    def __init__(self):
        self.tickets = Dummy()
        self.orders = Dummy()
        self.users = Dummy()


class WhmcsFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.whmcs"
        self.logger = j.logger.get('j.clients.whmcs')

    def get(self,
            username='',
            md5_password='',
            accesskey='',
            url='',
            cloudspace_product_id='',
            operations_user_id='',
            operations_department_id='',
            instance='main'):

        return WhmcsInstance(username,
                             md5_password,
                             accesskey,
                             url,
                             cloudspace_product_id,
                             operations_user_id,
                             operations_department_id,
                             instance)

    def getDummy(self):
        return DummyWhmcs()
