from JumpScale import j

import Models
import inspect

try:
    import mongoengine
except:
    pass


#@this is not ok, we should never run any service automatically, only exception is 
# if not j.sal.process.checkProcessRunning('mongod'):
#     j.sal.process.execute(
#         "mongod --fork --logpath /opt/jumpscale8/var/mongodb.log")

class NameSpaceLoader():
    def __init__(self, modelsmodule):
        self._module = modelsmodule
        mongoengine.register_connection(self._module.DB, self._module.DB)
        self._getModels()

    def _getModels(self):
        self._models = list()
        for name, mem in inspect.getmembers(self._module, inspect.isclass):
            if mongoengine.document.Document and Models.ModelBase in inspect.getmro(mem):
                self._models.append(name)
                self.__dict__[name] = mem

    def listModels(self):
        return self._models

    def connect2mongo(self, host='localhost', port=27017, db='jumpscale_system'):
        """
        """
        mongoengine.connect(db=db, host=host, port=port)


class System(NameSpaceLoader):
    def __init__(self):
        self.__jslocation__ = "j.data.models.system"
        super(System, self).__init__(Models)
