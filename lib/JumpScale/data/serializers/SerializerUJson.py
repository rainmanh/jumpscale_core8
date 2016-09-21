try:
    import ujson as json
except:
    import json
from SerializerBase import *


class SerializerUJson(SerializerBase):

    def __init__(self):
        self.__jslocation__ = "j.data.serializer.json"

    def dumps(self, obj, sort_keys=False, indent=False):
        return json.dumps(obj, ensure_ascii=False, sort_keys=sort_keys, indent=indent)

    def loads(self, s):
        if isinstance(s, bytes):
            s = s.decode('utf-8')
        return json.loads(s)
