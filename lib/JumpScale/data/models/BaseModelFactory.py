from JumpScale import j

from Models import *

try:
    import mongoengine
except:
    pass


#@this is not ok, we should never run any service automatically, only exception is 
# if not j.sal.process.checkProcessRunning('mongod'):
#     j.sal.process.execute(
#         "mongod --fork --logpath /opt/jumpscale8/var/mongodb.log")



class BaseModelFactory():

    def __init__(self):
        self.__jslocation__ = "j.data.models"

    DoesNotExist = DoesNotExist

    def connect2mongo(self, addr='localhost', port=27017, db='jumpscale'):
        """
        @todo (*2*)
        """
        try:
            mongoengine.connection.get_connection()
        except:
            mongoengine.connect(db='jumpscale_system')
                

    @property
    def Machine(self):
        return ModelMachine

    @property
    def Base(self):
        return ModelBase

    @property
    def ErrorCondition(self):
        return ModelErrorCondition

    @property
    def Grid(self):
        return ModelGrid

    @property
    def Group(self):
        return ModelGroup

    @property
    def Job(self):
        return ModelJob

    @property
    def Command(self):
        return ModelCommand

    @property
    def Audit(self):
        return ModelAudit

    @property
    def Disk(self):
        return ModelDisk

    @property
    def Alert(self):
        return ModelAlert

    @property
    def Heartbeat(self):
        return ModelHeartbeat

    @property
    def Jumpscript(self):
        return ModelJumpscript

    @property
    def Nic(self):
        return ModelNic

    @property
    def Node(self):
        return ModelNode

    @property
    def Process(self):
        return ModelProcess

    @property
    def Test(self):
        return ModelTest

    @property
    def User(self):
        return ModelUser

    @property
    def SessionCache(self):
        return ModelSessionCache

    def authenticate(self, username, passwd):
        um = self.User
        if um.objects(__raw__={'name': username, 'passwd': {'$in': [passwd, j.tools.hash.md5_string(passwd)]}}):
            return True
        return False
