from GogsClient import GogsClient
from JumpScale import j


class GogsFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.gogs"
        self.logger = j.logger.get("j.clients.gogs")

    def get(self, addr='https://192.168.1.1', port=443, login='abdu', passwd='gig1234'):
        return GogsClient(addr=addr, port=port, login=login, passwd=passwd)
