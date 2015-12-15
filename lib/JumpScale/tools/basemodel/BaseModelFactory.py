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
        key = "models.%s" % ttype
        return key

    def get(self, modelclass, id):
        modelname = modelclass._class_name
        key = self.getKeys(modelname)
        key = '%s_%s' % (key, id)
        modelraw = j.core.db.get(key.encode('utf-8'))
        if modelraw:
            modelraw = modelraw.decode()
            model = modelclass.from_json(modelraw)
            return model
        else:
            try:
                return modelclass.objects.get(guid=id)
            except DoesNotExist:
                return None

    def set(self, modelobject):
        key = self.getKeys(modelobject._class_name)
        key = '%s_%s' % (key, modelobject.guid)
        meta = modelobject._meta['indexes']
        expirey = meta[0].get('expireAfterSeconds', None) if meta else None
        modelraw = json.dumps(modelobject.to_dict())
        j.core.db.set(key, modelraw)
        if expirey:
            j.core.db.expire(key, expirey)

    def load(self, modelobject):
        key = self.getKeys(modelobject._class_name)

        if j.core.db.exists('%s_%s' % (key, modelobject.guid)):
            model = self.get(modelobject)
        else:
            model = self.set(modelobject)
        return model

    def find(self, model, query):
        return model.objects(__raw__=query)

    def remove(self, model, key):
        pass

    def exists(self, model, key):
        modelname = modelclass._class_name
        key = self.getKeys(modelname)
        if j.core.db.exists('%s_%s' % (key, id)):
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
