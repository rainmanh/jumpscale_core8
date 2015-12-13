
import blosc

class SerializerBlosc(object):
    def __init__(self):
        self.__jslocation__ = "j.data.serializer.blosc"    
    def dumps(self,obj):        
        return  blosc.compress(obj, typesize=8)
    def loads(self,s):
        return blosc.decompress(s)