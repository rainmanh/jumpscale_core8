
__all__ = ['IPv4Address', 'IPv4Range']

from JumpScale import j

# from JumpScale.core.types.IPAddress import IPv4Address, IPv4Range

# j.core.types.ipv4=IPv4Address()
# j.core.types.ipv4range=IPv4Range()

__all__ += ['Boolean', 'Integer', 'Float', 'String']
from JumpScale.core.types.PrimitiveTypes import Boolean, Integer, Float, String

j.core.types.bool=Boolean()
j.core.types.integer=Integer()
j.core.types.float=Float()
j.core.types.string=String()

__all__ += ['List', 'Set', 'Dictionary']
from JumpScale.core.types.CollectionTypes import List, Set, Dictionary

j.core.types.dict=Dictionary()
j.core.types.list=List()
j.core.types.set=Set()


# __all__ += ['Guid', 'Path', 'DirPath', 'FilePath', 'UnixDirPath',
#             'UnixFilePath', 'WindowsDirPath', 'WindowsFilePath', ]
# from JumpScale.core.types.CustomTypes import Guid, Path, DirPath, FilePath, \
#         UnixDirPath, UnixFilePath, WindowsDirPath, WindowsFilePath

# __all__ += ['Object', 'Enumeration']
# from JumpScale.core.types.GenericTypes import Object, Enumeration

# Type registration starts here

# def register_types():
#     '''Register all known types on some container

#     @return: Container with all types as attributes
#     @rtype: object
#     '''

#     #All modules we want to load types from
#     #This is inline not to clutter package namespace
#     from JumpScale.core.types import PrimitiveTypes, CollectionTypes, CustomTypes
#     TYPEMODS = (PrimitiveTypes, CollectionTypes, CustomTypes, )

#     class TypeContainer: pass
#     base = TypeContainer()

#     def _register_types_from_module(mod, base):
#         '''Hook all classes found in mod on base

#         This is an inner-function so we don't pollute package namespace.

#         @param mod: Module containing types to hook
#         @type mod: module
#         @param base: Hook point for types
#         @type base: object

#         @raises RuntimeError: Multiple types with the same name are found
#         '''
#         #Import inspect here so we don't pollute package namespace
#         import inspect

#         #Go through all names defined in the module (classes, imported modules,
#         #functions,...)
#         #Using names 'classname' and 'class_', although not all discovered
#         #attributes are classes... This will be a first discriminator though
#         for class_ in list(mod.__dict__.values()):
#             #Check whether it's a class defined in our module (not imported)
#             if inspect.isclass(class_) and inspect.getmodule(class_) is mod:
#                 #Fail on duplicate names
#                 if hasattr(base, class_.NAME):
#                     raise RuntimeError('Type %s is already registred on type base' % class_.NAME)
#                 #Hook the class
#                 setattr(base, class_.NAME, class_)

#     for mod in TYPEMODS:
#         _register_types_from_module(mod, base)


#     #This is similar to _register_types_from_module
#     def _register_generic_types_from_module(mod, base):
#         import inspect
#         for function in list(mod.__dict__.values()):
#             if inspect.isfunction(function) and inspect.getmodule(function) is mod:
#                 if hasattr(function, 'qtypename'):
#                     if hasattr(base, function.qtypename):
#                         raise RuntimeError('Type %s is already registered on type base' % function.qtypename)
#                     setattr(base, function.qtypename, function)

#     from JumpScale.core.types import GenericTypes
#     GENERICMODS = (GenericTypes, )
#     for mod in GENERICMODS:
#         _register_generic_types_from_module(mod, base)

#     return base
