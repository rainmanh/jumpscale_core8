

import snappy
from SerializerBase import *


class SerializerSnappy(SerializerBase):

    def __init__(self):
        self.__jslocation__ = "j.data.serializer.snappy"

    def dumps(self, obj):
        return snappy.compress(obj)

    def loads(self, s):
        return snappy.decompress(s)
