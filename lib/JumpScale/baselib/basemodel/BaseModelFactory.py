from JumpScale import j

from .Models import *
import mongoengine

try:
    mongoengine.connection.get_connection()
except mongoengine.ConnectionError:
    mongoengine.connect('jumpscale')


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

    def getSessionCacheModel(self):
        return ModelSessionCache

    def getKey(self, model):
        """
        @return hsetkey,key
        """
        ttype = model.split(".")[-1].replace("Model", "").lower()
        hsetkey = "models.%s" % ttype
        return hsetkey

    def get(self, model, key):
        hsetkey = getKey(model)
        modelraw = j.core.redis.hget(hsetkey, key).decode()
        model = model.from_json(modelraw)
        return model

    def set(self, model):
        modelclass = model._cls
        model.clean()
        hsetkey = self.getKey(modelclass)
        modelraw = json.dumps(model.to_dict())
        j.core.redis.hset(hsetkey, model.id, modelraw)

    def load(self, model):
        hsetkey = self.getKey(model._cls)
        if j.core.redis.hexists(hsetkey, model.id):
            model = self.get(model)
        else:
            self.set(model)
        return model

    def remove(self, model, key):
        hsetkey = self.getKey(model)
        if j.core.redis.hexists(hsetkey, key):
            j.core.redis.hdel(hset, key)
        # TODO ---> delete from mongo as well

    def find(self, model, query):
        if not query:
            query = {}
        return model.objects(__raw__=query)

    def exists(self, model, key):
        hsetkey = getKey(model)
        return j.core.redis.hexists(hsetkey, key)

    def authenticate(self, name, passwd):
        """
        authenticates a user and returns the groups in which the user is
        """
        query = {'id': name, 'active': True}
        results = self.find(self.getUserModel(), query)
        if not results:
            return {"authenticated": False, "exists": False}

        userguid = results[0]['guid']
        user = self.get(self.getUserModel(), userguid)

        if user["passwd"] == j.tools.hash.md5_string(passwd) or user["passwd"] == passwd:
            return {"authenticated": True, "exists": True, "groups": user["groups"],
                    "passwdhash": user["passwd"], "authkey": user["authkey"]}

        return {"authenticated": False, "exists": True}
