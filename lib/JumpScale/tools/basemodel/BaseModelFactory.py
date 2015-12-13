from JumpScale import j

from Models import *

import mongoengine
try:
    mongoengine.connection.get_connection()
except:
    mongoengine.connect(db='jumpscale_system')


class BaseModelFactory():

    def __init__(self):
        self.__jslocation__ = "j.core.models"

    def getBaseModel(self):
        return ModelBase

    def getErrorConditionModel(self):
        return ModelErrorCondition

    def getGridModel(self):
        return ModelGrid

    def getGroupModel(self):
        return ModelGroup

    def getJobModel(self):
        return ModelJob

    def getAuditModel(self):
        return ModelAudit

    def getDiskModel(self):
        return ModelDisk

    def getAlertModel(self):
        return ModelAlert

    def getHeartbeatModel(self):
        return ModelHeartbeat

    def getJumpscriptModel(self):
        return ModelJumpscript

    def getMachineModel(self):
        return ModelMachine

    def getNicModel(self):
        return ModelNic

    def getNodeModel(self):
        return ModelNode

    def getProcessModel(self):
        return ModelProcess

    def getTestModel(self):
        return ModelTest

    def getUserModel(self):
        return ModelUser

    def getSessionCacheModel(self):
        return ModelSessionCache

    def getKeys(self, modelname):
        """
        @return hsetkey,key
        """
        ttype = modelname.split(".")[-1].replace("Model", "").lower()
        hsetkey = "models.%s" % ttype
        return hsetkey

    def get(self, modelclass, id):
        modelname = modelclass._class_name
        hsetkey = self.getKeys(modelname)
        modelraw = j.core.db.hget(hsetkey, id)
        if modelraw:
            modelraw = modelraw.decode()
        else:
            try:
                modelclass.objects.get(id=id)
            except DoesNotExist:
                return None
        model = model.from_json(modelraw)
        return model

    def set(self, modelobject):
        hsetkey = self.getKeys(modelobject._class_name)
        modelraw = json.dumps(modelobject.to_dict())
        j.core.db.hset(hsetkey, modelobject.id, modelraw)

    def load(self, modelobject):
        hsetkey = self.getKeys(modelobject._class_name)

        if j.core.db.hexists(hsetkey, modelobject.id):
            model = self.get(modelobject)
        else:
            self.set(modelobject)
        return model

    def find(self, model, query):
        return model.objects(__raw__=query)

    def remove(self, model, key):
        pass

    def exists(self, model, key):
        modelname = modelclass._class_name
        hsetkey = self.getKeys(modelname)
        if j.core.db.hexists(hsetkey, id):
            return True
        try:
            modelclass.objects.get(id=id)
        except DoesNotExist:
            return False

    def authenticate(self, username, passwd):
        um = self.getUserModel()
        if um.objects(__raw__={'name': username, 'passwd': {'$in': [passwd, j.tools.hash.md5_string(passwd)]}}):
            return True
        return False
