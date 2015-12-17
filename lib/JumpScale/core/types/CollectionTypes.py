

'''Definition of several collection types (list, dict, set,...)'''

import types

# from JumpScale.core.types.base import BaseType, NO_DEFAULT

class Dictionary():
    def __init__(self):
        self.__jslocation__ = "j.core.types.dict"

    '''Generic dictionary type'''
    NAME = 'dictionary'

    @staticmethod
    def check(value):
        '''Check whether provided value is a dict'''
        return isinstance(value, dict)

    def get_default(self, obj):
        if self._default is NO_DEFAULT:
            return dict()
        return dict(self._default)


class List():
    def __init__(self):
        self.__jslocation__ = "j.core.types.list"

    '''Generic list type'''
    NAME = 'list'

    @staticmethod
    def check(value):
        '''Check whether provided value is a list'''
        return isinstance(value, list)
    
    def get_default(self, obj):
        if self._default is NO_DEFAULT:
            return list()
        return list(self._default)

class Set():
    def __init__(self):
        self.__jslocation__ = "j.core.types.set"

    '''Generic set type'''
    NAME = 'set'

    @staticmethod
    def check(value):
        '''Check whether provided value is a set'''
        return isinstance(value, set)