from JumpScale import j

import capnp

import model_job_capnp as ModelCapnp

from .JobModel import JobModel
from .ActionModel import ActionModel
from .RunModel import RunModel

defaultConfig = {
    'redis': {
        'unixsocket': '/tmp/ays.sock'
    }
}


class ModelsFactory():

    def __init__(self):
        self._config_path = j.sal.fs.joinPaths(j.dirs.cfgDir, 'ays/ays.conf')
        config = self._load_config(self._config_path)

        self.namespacePrefix = "jobs"
        ModelFactory = j.data.capnp.getModelFactoryClass()

        self.capnpModel = ModelCapnp

        self.job = ModelFactory(self, "Job", JobModel, **config['redis'])
        self.action = ModelFactory(self, "Action", ActionModel, **config['redis'])
        self.run = ModelFactory(self, "Run", RunModel, **config['redis'])

    def destroy(self):
        self.job.destroy()
        self.action.destroy()
        self.run.destroy()

    def _load_config(self, path):
        if not j.sal.fs.exists(path):
            return defaultConfig

        cfg = j.data.serializer.toml.load(path)
        if 'redis' not in cfg:
            return defaultConfig

        return cfg
