from JumpScale import j


class Client:
    def __init__(self, host='localhost', port=6379, unixsocket=None):
        self.host = host
        self.port = port
        self.unixsocket = unixsocket
        self._server = j.servers.kvs.getRedisStore("ays_server", namespace='db', host=self.host, port=self.port, unixsocket=self.unixsocket)
        self.logger = j.logger.get('j.clients.atyourservice')

    def _do(self, command, args={}):
        request = {"command": command}
        request.update(args)
        request = j.data.serializer.json.dumps(request)
        self._server.queuePut('command', request)

    def execute_action(self, service, action, args={}):
        """
        @param service: service object you want to execute action on
        @type service: JumpScale.baselib.atyourservice81.Service.Service
        @param action: name of the action you want to execute. string
        @type action: string
        @param args: arguement to pass to the action
        @type args: dict
        """
        self._do('execute', {
            'repo_path': service.aysrepo.path,
            'service_key': service.model.key,
            'action': action,
            'args': args
        })

    def send_event(self, event, args={}):
        """
        @param event: type of the event.
        @type event: string
        @param args: payload of the event
        @type args: dict
        """
        self._do('event', {
            'event': event,
            'args': args
        })
