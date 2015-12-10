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

    def getKeys(self, modelname, id):
        """
        @return hsetkey,key
        """
        ttype = modelname.split(".")[-1].replace("Model", "").lower()
        hsetkey = "models.%s" % ttype
        return (hsetkey, id)

    def get(self, modelclass, id):
        modelname = modelclass._class_name
        hsetkey = self.getKeys(modelname, id)
        modelraw = j.core.db.hget(hsetkey, id).decode()
        model = model.from_json(modelraw)
        return model

    def set(self, modelobject):
        hsetkey, key = self.getKeys(modelobject._class_name, modelobject.id)
        modelraw = json.dumps(modelobject.to_dict())
        j.core.db.hset(hsetkey, key, modelraw)

    def load(self, modelobject):
        hsetkey, key = self.getKeys(modelobject._class_name, modelobject.id)

        if j.core.db.hexists(hsetkey, key):
            model = self.get(modelobject)
        else:
            self.set(modelobject)
        return model

    def find(self, model, query):
        return model.objects(__raw__=query)
