from JumpScale import j

import capnp
import model_capnp as ModelCapnp

from .ActorModel import ActorModel
from .ServiceModel import ServiceModel
from .RepoModel import RepoModel

if "darwin" in str(j.core.platformtype.myplatform):
    socket=j.core.db.config_get()["unixsocket"]
else:
    socket='/tmp/ays.sock'

defaultConfig = {
    'redis': {
        'unixsocket': socket
    }
}


class ModelsFactory():

    def __init__(self, aysrepo=None):
        self._config_path = j.sal.fs.joinPaths(j.dirs.cfgDir, 'ays/ays.conf')
        config = self._load_config(self._config_path)

        ModelFactory = j.data.capnp.getModelFactoryClass()
        self.capnpModel = ModelCapnp
        self.namespacePrefix = "ays:"
        self.repo = ModelFactory(self, "Repo", RepoModel, **config['redis'])
        if aysrepo:
            self.namespacePrefix = "ays:%s" % aysrepo.name
            self.actor = ModelFactory(self, "Actor", ActorModel, **config['redis'])
            self.service = ModelFactory(self, "Service", ServiceModel, **config['redis'])
            self.actor.repo = aysrepo
            self.service.repo = aysrepo

    def _load_config(self, path):
        if not j.sal.fs.exists(path):
            return defaultConfig

        cfg = j.data.serializer.toml.load(path)
        if 'redis' not in cfg:
            return defaultConfig

        return cfg

    def destroy(self):
        self.repo.destroy()
        self.actor.destroy()
        self.service.destroy()
