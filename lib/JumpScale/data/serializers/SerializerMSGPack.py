
import msgpack
from SerializerBase import *


class SerializerMSGPack(SerializerBase):

    def __init__(self):
        self.__jslocation__ = "j.data.serializer.msgpack"

    def dumps(self, obj):
        return msgpack.packb(obj,use_bin_type=True)

    def loads(self, s):
        return msgpack.unpackb(s,encoding="utf-8")
