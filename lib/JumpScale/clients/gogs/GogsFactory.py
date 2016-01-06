from GogsClient import GogsClient
from JumpScale import j


class GogsFactory:
    def __init__(self):
        self.__jslocation__ = "j.clients.gogs"
        j.logger.consolelogCategories.append("gogs")
    
    def get(self, addr='http://172.17.0.3', port='3000', login='abdu', passwd='gig1234'):
        return GogsClient(addr, port, login, passwd)
