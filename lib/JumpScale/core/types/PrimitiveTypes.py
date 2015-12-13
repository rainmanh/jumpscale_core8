

'''Definition of several primitive type properties (integer, string,...)'''


class Boolean():
    def __init__(self):
        self.__jslocation__ = "j.core.types.bool"

    '''Generic boolean type'''
    NAME = 'boolean'

    @staticmethod
    def fromString(s):
        if isinstance(s, bool):
            return s

        s = str(s)
        if s.upper() in ('0', 'FALSE'):
            return False
        elif s.upper() in ('1', 'TRUE'):
            return True
        else:
            raise ValueError("Invalid value for boolean: '%s'" % s)

    @staticmethod
    def checkString(s):
        try:
            Boolean.fromString(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def toString(boolean):
        return str(boolean)

    @staticmethod
    def check(value):
        '''Check whether provided value is a boolean'''
        return value is True or value is False

class Integer():
    def __init__(self):
        self.__jslocation__ = "j.core.types.integer"

    '''Generic integer type'''
    NAME = 'integer'


    @staticmethod
    def checkString(s):
        return s.isdigit()

    @staticmethod
    def check(value):
        '''Check whether provided value is an integer'''
        return isinstance(value, int)

class Float():
    def __init__(self):
        self.__jslocation__ = "j.core.types.float"

    '''Generic float type'''
    NAME = 'float'

    @staticmethod
    def checkString(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def check(value):
        '''Check whether provided value is a float'''
        return isinstance(value, float)

class String():
    def __init__(self):
        self.__jslocation__ = "j.core.types.string"

    '''Generic string type'''
    NAME = 'string'

    @staticmethod
    def fromString(s):
        return s

    @staticmethod
    def toString(v):
        return v

    @staticmethod
    def check(value):
        '''Check whether provided value is a string'''
        return isinstance(value, str)
