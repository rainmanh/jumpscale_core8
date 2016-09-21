from GogsClient import GogsClient
from JumpScale import j


class GogsFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.gogs"
        self.logger = j.logger.get("j.clients.gogs")

    def get(self, addr='http://172.17.0.1', port='3000', login='abdu', passwd='gig1234'):
        return GogsClient(addr, port, login, passwd)
