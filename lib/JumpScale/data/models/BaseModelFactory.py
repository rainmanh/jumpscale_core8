from JumpScale import j

import Models
import inspect

try:
    import mongoengine
except:
    pass


class NameSpaceLoader():
    def __init__(self, modelsmodule):
        self._module = modelsmodule
        mongoengine.register_connection(self._module.DB, self._module.DB)
        self._getModels()

    def _getModels(self):
        self._models = list()
        self._modelspecs = dict()
        for name, mem in inspect.getmembers(self._module, inspect.isclass):
            if issubclass(mem, mongoengine.base.document.BaseDocument) and mongoengine.Document != inspect.getmro(mem)[0]:
                self._models.append(name)
                self._modelspecs[name] = mem
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
