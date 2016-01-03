try:
    import ujson as json
except:
    import json


class SerializerUJson(object):
    def __init__(self):
        self.__jslocation__ = "j.data.serializer.json"

    def dumps(self,obj):
        return json.dumps(obj, ensure_ascii=False)

    def loads(self,s):
        if isinstance(s,bytes):
            s=s.decode('utf-8')
        return json.loads(s)
