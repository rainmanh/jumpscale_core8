
import toml

from SerializerBase import *


class SerializerTOML(SerializerBase):

    def __init__(self):
        self.__jslocation__ = "j.data.serializer.toml"

    def dumps(self, obj):
        return toml.dumps(obj)

    def loads(self, s):
        if isinstance(s, bytes):
            s = s.decode('utf-8')
        return toml.loads(s)
