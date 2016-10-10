from JumpScale import j

import capnp
import model_capnp as ModelCapnp

from .ActorModel import ActorModel
from .ServiceModel import ServiceModel
from .RepoModel import RepoModel

defaultConfig = {
    'redis': {
        'unixsocket': '/tmp/ays.sock'
    }
}


class ModelsFactory():

    def __init__(self, aysrepo=None):
        self._config_path = j.sal.fs.joinPaths(j.dirs.cfgDir, 'ays/ays.conf')
        config = self._load_config(self._config_path)

        ModelFactory = j.data.capnp.getModelFactoryClass()
        self.capnpModel = ModelCapnp
        if not aysrepo:
            self.namespacePrefix = "ays:"
            self.repo = ModelFactory(self, "Repo", RepoModel, **config['redis'])
        else:
            self.namespacePrefix = "ays:%s" % aysrepo.name

            self.actor = ModelFactory(self, "Actor", ActorModel, **config['redis'])
            self.service = ModelFactory(self, "Service", ServiceModel, **config['redis'])

            self.actor.repo = aysrepo
            self.service.repo = aysrepo

    def _load_config(self, path):
        if not j.sal.fs.exists(path):
            return defaultConfig
        return j.data.serializer.toml.load(path)

    def destroy(self):
        self.actor.destroy()
        self.service.destroy()
