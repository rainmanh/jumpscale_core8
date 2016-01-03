from JumpScale import j

from Models import *

import mongoengine

if not j.sal.process.checkProcessRunning('mongod'):
    j.sal.process.execute(
        "mongod --fork --logpath /opt/jumpscale8/var/mongodb.log")

try:
    mongoengine.connection.get_connection()
except:
    mongoengine.connect(db='jumpscale_system')


class BaseModelFactory():

    def __init__(self):
        self.__jslocation__ = "j.data.models"

    DoesNotExist = DoesNotExist

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


    def delete(self, model, key, redis=True):
        raise RuntimeError("not implemented")
        pass

    def exists(self, model, guid=None, redis=True):
        if redis:
            if guid == None:
                guid = model.guid
            modelname = model._class_name
            key = self.getKey(modelname, guid)
            if j.core.db.exists('%s_%s' % (key, guid)):
                return True
            else:
                return False
        else:
            if guid == None:
                raise RuntimeError("guid cannot be None")
            try:
                model.objects.get(guid=guid)
            except DoesNotExist:
                return False

    def authenticate(self, username, passwd):
        um = self.User
        if um.objects(__raw__={'name': username, 'passwd': {'$in': [passwd, j.tools.hash.md5_string(passwd)]}}):
            return True
        return False
