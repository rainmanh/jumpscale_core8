

'''Definition of several collection types (list, dict, set,...)'''

import types

# from JumpScale.core.types.base import BaseType, NO_DEFAULT

class Dictionary():
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
    '''Generic set type'''
    NAME = 'set'

    @staticmethod
    def check(value):
        '''Check whether provided value is a set'''
        return isinstance(value, set)