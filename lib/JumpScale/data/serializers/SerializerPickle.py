
import pickle

from SerializerBase import *


class SerializerPickle(SerializerBase):

    def __init__(self):
        self.__jslocation__ = "j.data.serializer.pickle"

    def dumps(self, obj):
        return pickle.dumps(obj)

    def loads(self, s):
        return pickle.loads(s)
