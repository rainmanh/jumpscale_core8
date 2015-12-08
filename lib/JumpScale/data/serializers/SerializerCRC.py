
import struct


class SerializerCRC(object):
    def __init__(self):
        pass
        #self.__jslocation__ = "j.data.serializer.crc"

    def dumps(self,obj):
        j.tools.hash.crc32_string(obj)
        return obj

    def loads(self,s):
        return s[4:]
