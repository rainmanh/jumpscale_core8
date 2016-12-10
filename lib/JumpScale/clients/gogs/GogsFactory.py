from GogsClient import GogsClient
from JumpScale import j

from JumpScale.clients.gogs.models import ModelsFactory


class GogsFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.gogs"
        self.logger = j.logger.get("j.clients.gogs")
        self.db = ModelsFactory()

    def get(self, addr='https://127.0.0.1', port=3000, login='root', passwd='root'):
        return GogsClient(addr=addr, port=port, login=login, passwd=passwd)

    def getDataFromPSQL(self, ipaddr="127.0.0.1", port=5432, login="gogs", passwd="something", dbname="gogs"):
        """
        get peewee model from psql database from gogs & then load in our capnp database
        """
        model = j.clients.peewee.getModel(ipaddr=ipaddr, port=port, login=login, passwd=passwd, dbname=dbname)
        print([item.name for item in model.Issue.select()])
        from IPython import embed
        print("DEBUG NOW ")
        embed()
        raise RuntimeError("stop debug here")
