

class SerializerInt:

    def __init__(self):
        self.__jslocation__ = "j.data.serializer.int"

    def dumps(self, obj):
        return str(obj)

    def loads(self, s):
        return int(s)
