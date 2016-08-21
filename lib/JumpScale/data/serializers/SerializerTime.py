
import struct


class SerializerTime:

    def __init__(self):
        self.__jslocation__ = "j.data.serializer.time"

    def dumps(self, obj):
        struct.pack('<i', j.data.time.getTimeEpoch())
        return obj

    def loads(self, s):
        epoch = struct.unpack('<i', s[0:2])
        return s[2:]
