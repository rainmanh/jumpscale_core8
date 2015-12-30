from JumpScale import j

'''Definition of several primitive type properties (integer, string,...)'''


class String():

    '''Generic string type'''
    NAME = 'string'
    BASETYPE = 'string'

    @staticmethod
    def fromString(s):
        """
        return string from a string (is basically no more than a check)
        """
        # if not isinstance(value, str):
        #     raise ValueError("Should be string:%s"%s)
        s=str(s)
        return s

    @staticmethod
    def toString(v):
        if String.check(v):
            return str(v)
        else:
            raise ValueError("Could not convert to string:%s"%v)

    @staticmethod
    def check(value):
        '''Check whether provided value is a string'''
        return isinstance(value, str)

    @staticmethod
    def get_default():
        return ""


class Boolean():

    '''Generic boolean type'''
    NAME = 'boolean'
    BASETYPE = 'boolean'

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
        if Boolean.check(s):
            return str(boolean)
        else:
            raise ValueError("Invalid value for boolean: '%s'" % boolean)

    @staticmethod
    def check(value):
        '''Check whether provided value is a boolean'''
        return value is True or value is False

    @staticmethod
    def get_default():
        return True
    

class Integer():

    '''Generic integer type'''
    NAME = 'integer'
    BASETYPE = 'integer'

    @staticmethod
    def checkString(s):
        return s.isdigit()

    @staticmethod
    def check(value):
        '''Check whether provided value is an integer'''
        return isinstance(value, int)

    @staticmethod
    def toString(value):
        if Integer.check(value):
            return str(value)
        else:
            raise ValueError("Invalid value for integer: '%s'" % value)

    @staticmethod
    def fromString(s):
        return j.data.text.getInt(s)

    @staticmethod
    def get_default():
        return 0


class Float():

    '''Generic float type'''
    NAME = 'float'
    BASETYPE = 'float'

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

    @staticmethod
    def toString(value):
        if Float.check(value):
            return str(value)
        else:
            raise ValueError("Invalid value for float: '%s'" % value)

    @staticmethod
    def fromString(s):
        return j.data.text.getFloat(s)

    @staticmethod
    def get_default():
        return 0.0


