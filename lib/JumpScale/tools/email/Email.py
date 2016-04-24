from JumpScale import j

import Sender


class Email:
    def __init__(self):
        self.__jslocation__ = "j.tools.email"

    def getLast(self, num=100):
        """
        Gets most recent `num` emails

        :return: list
        """
        raise NotImplementedError()

    def pop(self):
        """
        Pops oldest email from the queue.

        :return: Message
        """
        raise NotImplementedError()

    def getSender(self, username, password, host='smtp.mandrillapp.com', port=587):
        return Sender.Sender(username, password, host, port)

    def getDefaultSender(self):
        """
        Gets the default configured email sender

        :return: Sender instance
        """
        cfg = j.data.serializer.yaml.load(j.sal.fs.joinPaths(j.dirs.cfgDir, 'smtp.yaml'))
        return self.getSender(cfg['username'], cfg['password'], cfg['host'], cfg['port'])
