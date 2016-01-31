

'''Definition of several collection types (list, dict, set,...)'''

from PrimitiveTypes import *

# from base import BaseType

class Dictionary():
    '''Generic dictionary type'''
    def __init__(self):
        self.NAME = 'dictionary'
        self.BASETYPE = 'dictionary'

    
    def check(self,value):
        '''Check whether provided value is a dict'''
        return isinstance(value, dict)

    
    def get_default(self):
        return dict()
        # if self._default is NO_DEFAULT:
        #     return dict()
        # return dict(self._default)


class List():

    '''Generic list type'''

    def __init__(self):
        self.NAME = 'list'
        self.BASETYPE = 'list'

    
    def check(self,value):
        '''Check whether provided value is a list'''
        return isinstance(value, list) or isinstance(value, tuple) 
    
    
    def get_default(self):
        return list()

    
    def clean(self,v,ttype="str"):
        if j.data.types.string.check(ttype):
            ttype=j.data.types.getTypeClass(ttype)
        if not j.data.types.string.check(v):
            if not j.data.types.list.check(v):
                raise ValueError("Input needs to be string or list:%s"%v)
            out=[]
            for item in v:
                item=ttype.fromString(item)                    
                out.append(item)
            v=out
        else:
            v=j.data.text.getList(v,ttype)
        return v

    
    def fromString(self,v,ttype="str"):
        v=self.clean(v,ttype)
        if self.check(v):
            return v
        else:
            raise ValueError("List not properly formatted.")        

    toString=fromString


class Set():

    '''Generic set type'''
    def __init__(self):
        self.NAME = 'set'
        self.BASETYPE = 'set'

    
    def check(self,value):
        '''Check whether provided value is a set'''
        return isinstance(value, set)

    
    def get_default(self):
        return list()
