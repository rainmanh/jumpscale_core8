

'''Definition of several collection types (list, dict, set,...)'''

from PrimitiveTypes import *

# from base import BaseType

class Dictionary():
    '''Generic dictionary type'''
    NAME = 'dictionary'
    BASETYPE = 'dictionary'

    @staticmethod
    def check(value):
        '''Check whether provided value is a dict'''
        return isinstance(value, dict)

    @staticmethod
    def get_default():
        return dict()
        # if self._default is NO_DEFAULT:
        #     return dict()
        # return dict(self._default)


class List():

    '''Generic list type'''
    NAME = 'list'
    BASETYPE = 'list'

    @staticmethod
    def check(value):
        '''Check whether provided value is a list'''
        return isinstance(value, list)
    
    @staticmethod
    def get_default():
        return list()

    @staticmethod
    def clean(v,ttype="str"):
        if not String.check(v):
            raise ValueError("Input needs to be string:%s"%v)
        v=j.data.text.getList(v,ttype)
        return v

    @staticmethod
    def fromString(v,ttype="str"):
        v=List.clean(v,ttype)
        if List.check(v):
            return v
        else:
            raise ValueError("List not properly formatted.")        

    toString=fromString


class Set():

    '''Generic set type'''
    NAME = 'set'
    BASETYPE = 'set'

    @staticmethod
    def check(value):
        '''Check whether provided value is a set'''
        return isinstance(value, set)

    @staticmethod
    def get_default():
        return list()
