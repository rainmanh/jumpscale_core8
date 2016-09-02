
# import struct
from JumpScale import j


class SerializerCRC:

    def __init__(self):
        self.__jslocation__ = "j.data.serializer.crc"

    def dumps(self, obj):
        j.data.hash.crc32_string(obj)
        return obj

    def loads(self, s):
        return s[4:]
