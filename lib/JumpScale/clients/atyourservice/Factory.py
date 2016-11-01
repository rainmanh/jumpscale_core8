from JumpScale.clients.atyourservice.Client import Client
from JumpScale import j

class Factory:

    def __init__(self):
        self.__jslocation__ = "j.clients.atyourservice"

    def get(self, host='localhost', port=6379, unixsocket=None):
        return Client(host=host, port=port, unixsocket=unixsocket)

    def getFromConfig(self, config_path):
        cfg = j.data.serializer.toml.load(config_path)
        if 'redis' not in cfg:
            raise j.exceptions.Input('format of the config file not valid. Missing redis section')
        return Client(host=cfg['redis']['host'], port=cfg['redis']['port'], unixsocket=cfg['redis']['unixsocket'])
