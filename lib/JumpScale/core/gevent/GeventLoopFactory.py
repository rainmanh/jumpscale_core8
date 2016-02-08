from JumpScale import j

from GeventLoop import GeventLoop
import time


class GeventLoopFactory():
    def __init__(self):
        self.__jslocation__ = "j.core.gevent"

    def getGeventLoopClass(self):
        return GeventLoop
