
import pylzma
from SerializerBase import *


class SerializerLZMA(SerializerBase):

    def __init__(self):
        self.__jslocation__ = "j.data.serializer.lzma"

    def dumps(self, obj):
        return pylzma.compress(obj)

    def loads(self, s):
        return pylzma.decompress(s)
