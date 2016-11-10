import yaml
# import cStringIO

from SerializerBase import *


class SerializerYAML(SerializerBase):

    def __init__(self):
        self.__jslocation__ = "j.data.serializer.yaml"

    def dumps(self, obj, default_flow_style=False):
        return yaml.dump(obj, default_flow_style=default_flow_style)

    def loads(self, s):
        # out=cStringIO.StringIO(s)
        return yaml.load(s)


# from JumpScale import j

# from yaml import load, dump
# try:
#     from yaml import CLoader as Loader, CDumper as Dumper
# except ImportError:
#     from yaml import Loader, Dumper


# class YAMLTool:
#     def decode(self,string):
#         """
#         decode yaml string to python object
#         """
#         return load(string)

#     def encode(self,obj,width=120):
#         """
#         encode python (simple) objects to yaml
#         """
#         return dump(obj, width=width, default_flow_style=False)
#
