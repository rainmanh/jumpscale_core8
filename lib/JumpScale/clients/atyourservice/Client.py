from JumpScale import j


class Client:
    def __init__(self, host='localhost', port=6379, unixsocket=None):
        self.host = host
        self.port = port
        self.unixsocket = unixsocket
        self._server = j.servers.kvs.getRedisStore("ays_server", namespace='db', host=self.host, port=self.port, unixsocket=self.unixsocket)
        self.logger = j.logger.get('j.clients.atyourservice')

    def do(self, command, args={}):
        request = {"command": command}
        request.update(args)
        request = j.data.serializer.json.dumps(request)
        self._server.queuePut('command', request)
