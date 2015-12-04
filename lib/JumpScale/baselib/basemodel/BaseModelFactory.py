from JumpScale import j

from .Models import *


class BaseModelFactory():

    def __init__(self):
        pass

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

    def getKeys(self,model):
        """
        @return hsetkey,key
        """
        ttype=model._cls.split(".")[-1].replace("Model","").lower()
        hsetkey="models.%s"%ttype
        model.clean()
        return (hsetkey,model.id)

    def get(self,model):
        hsetkey,key=self.getKeys(model)
        modelraw=j.core.redis.hget(hsetkey,key).decode()
        model=model.from_json(modelraw)
        return model

    def set(self,model):
        hsetkey,key=self.getKeys(model)
        modelraw=json.dumps(model.to_dict())
        j.core.redis.hset(hsetkey,key,modelraw)

    def load(self,model):
        hsetkey,key=self.getKeys(model)
        
        if j.core.redis.hexists(hsetkey,key):
            model = self.get(model)
        else:
            self.set(model)
        return model

