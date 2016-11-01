from JumpScale import j

import capnp

import model_gogs_capnp as ModelCapnp

from .IssueModel import IssueModel
from .UserModel import UserModel
from .RepoModel import RepoModel

defaultConfig = {
    'redis': {
        'unixsocket': '/tmp/ays.sock'
    }
}


class ModelsFactory():

    def __init__(self):
        self._config_path = j.sal.fs.joinPaths(j.dirs.cfgDir, 'ays/ays.conf')
        config = self._load_config(self._config_path)

        self.namespacePrefix = "gogs"
        ModelFactory = j.data.capnp.getModelFactoryClass()

        self.capnpModel = ModelCapnp

        self.issue = ModelFactory(self, "Issue", IssueModel, **config['redis'])
        self.user = ModelFactory(self, "User", UserModel, **config['redis'])
        self.repo = ModelFactory(self, "Repo", RepoModel, **config['redis'])

    def destroy(self):
        self.issue.destroy()
        self.user.destroy()
        self.repo.destroy()

    def _load_config(self, path):
        if not j.sal.fs.exists(path):
            return defaultConfig

        cfg = j.data.serializer.toml.load(path)
        if 'redis' not in cfg:
            return defaultConfig

        return cfg
