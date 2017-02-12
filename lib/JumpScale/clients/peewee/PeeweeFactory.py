from JumpScale import j
import os
try:
    import psycopg2
except:
    os.system("pip3 install psycopg2")
    import psycopg2

try:
    import peewee
except:
    os.system("pip3 install peewee")
    import peewee

from Pwiz import Pwiz

import importlib


class PeeweeFactory:
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.peewee"
        self.clients = {}

    # def getClient(self, ipaddr="localhost", port=5432, login="postgres", passwd="rooter", dbname="template"):
    #     key = "%s_%s_%s_%s_%s" % (ipaddr, port, login, passwd, dbname)
    #     if key not in self.clients:
    #         self.clients[key] = PostgresClient(
    #             ipaddr, port, login, passwd, dbname)
    #     return self.clients[key]

    # def getModelDoesntWorkYet(self, ipaddr="localhost", port=5432, login="postgres", passwd="rooter", dbname="template", dbtype="postgres", schema=None, cache=True):
    #     key = "%s_%s_%s_%s_%s" % (ipaddr, port, login, dbname, dbtype)
    #     if key not in self._cacheModel:
    #         pw = Pwiz(host=ipaddr, port=port, user=login, passwd=passwd, dbtype=dbtype, schema=schema, dbname=dbname)
    #         self._cacheModel[key] = pw.codeModel
    #     code = self._cacheModel[key]
    #     from IPython import embed
    #     print("DEBUG NOW ooo")
    #     embed()
    #     raise RuntimeError("stop debug here")

    def resetCache(self):
        for item in j.core.db.keys("peewee.*"):
            j.core.db.delete(item)

    def getModel(self, ipaddr="localhost", port=5432, login="postgres", passwd="rooter", dbname="template", dbtype="postgres", schema=None, cache=True):
        """
        example usage:
            model=j.clients.peewee.getModel(login="gogs",passwd="something",dbname="gogs")
            print([item.name for item in model.Issue.select()])
        """
        key = "%s_%s_%s_%s_%s" % (ipaddr, port, login, dbname, dbtype)

        if j.core.db.get("peewee.code.%s" % key) == None:
            cmd = 'pwiz.py -H %s  -p %s -u "%s" -P -i %s' % (ipaddr, port, login, dbname)
            rc, out,err = j.sal.process.execute(cmd, useShell=True, die=True, showout=False)
            j.core.db.set("peewee.code.%s" % key, out)
        code = j.core.db.get("peewee.code.%s" % key).decode()

        path = j.sal.fs.joinPaths(j.dirs.TMPDIR, "peewee", key + ".py")
        j.sal.fs.createDir(j.sal.fs.joinPaths(j.dirs.TMPDIR, "peewee"))
        j.sal.fs.writeFile(path, code)

        loader = importlib.machinery.SourceFileLoader(key, path)
        module = loader.load_module(key)

        return module
