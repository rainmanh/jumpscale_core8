from JumpScale import j
'''Definition of several custom types (paths, ipaddress, guid,...)'''

import re

from PrimitiveTypes import *


GUID_RE = re.compile('^[0-9a-fA-F]{8}[-:][0-9a-fA-F]{4}[-:][0-9a-fA-F]{4}[-:][0-9a-fA-F]{4}[-:][0-9a-fA-F]{12}$')
class Guid(String):
    '''Generic GUID type'''
    NAME = 'guid'

    @staticmethod
    def check(value):
        '''Check whether provided value is a valid GUID string'''
        if not String.check(value):
            return False
        return GUID_RE.match(value) is not None

    @staticmethod
    def get_default():
        return j.data.idgenerator.generateGUID()

    @staticmethod
    def fromString(v):
        if not String.check(v):
            raise ValueError("Input needs to be string:%s"%v)
        if Guid.check(s):
            return s
        else:
            raise ValueError("%s not properly formatted."%self.NAME)        

    toString=fromString


class Path(String):
    '''Generic path type'''
    NAME = 'path'

    @staticmethod
    def check(value):
        '''Check whether provided value is a valid path

        This checks whether value is a valid string only.
        '''
        return String.check(value)

    @staticmethod
    def fromString(v):
        if not String.check(v):
            raise ValueError("Input needs to be string:%s"%v)
        if Guid.check(s):
            return s
        else:
            raise ValueError("%s not properly formatted."%self.NAME)       

    toString=fromString

    @staticmethod
    def get_default():
        return ""


#@todo (*1*) need better regex
class Email(String):
    """
    """
    NAME = 'email'
    _RE = re.compile('^[0-9a-z.@_\-]*')

    @staticmethod
    def check(value):
        '''
        Check whether provided value is a valid tel nr
        '''
        if not String.check(value):
            return False
        value=Email.clean(value)
        return Email._RE.fullmatch(value) is not None

    @staticmethod
    def clean(v):
        if not String.check(v):
            raise ValueError("Input needs to be string:%s"%v)
        v=v.lower()
        v.strip()
        return v

    @staticmethod
    def fromString(v):
        v=Email.clean(v)
        if Email.check(v):
            return v
        else:
            raise ValueError("%s not properly formatted."%self.NAME)        

    toString=fromString

    @staticmethod
    def get_default():
        return "changeme@example.com"

class Tel(Email):
    """
    format is e.g. +32 475.99.99.99
    only requirement is it needs to start with +
    the. & , and spaces will not be remembered
    """
    NAME = 'tel'
    _RE = re.compile('\+[0-9]*')

    @staticmethod
    def clean(v):
        if not String.check(v):
            raise ValueError("Input needs to be string:%s"%v)
        v=v.replace(".","")
        v=v.replace(",","")
        v=v.replace(" ","")
        v.strip()
        return v

    @staticmethod
    def get_default():
        return "+32 475.99.99.99"


#@todo (*1*) need better regex
class IPRange(Email):
    """
    """
    NAME = 'IPRANGE'
    _RE = re.compile('.*')

    @staticmethod
    def get_default():
        return "changeme@example.com"

#@todo (*1*) need better regex
class IPAddress(Email):
    """
    """
    NAME = 'IPRANGE'
    _RE = re.compile('.*')

    @staticmethod
    def get_default():
        return "192.168.1.1"

class IPPort(Integer):
    '''Generic IP port type'''
    NAME = 'ipport'
    BASETYPE = 'string'
    
    @staticmethod
    def check(value):
        '''
        Check if the value is a valid port
        We just check if the value a single port or a range
        Values must be between 0 and 65535
        '''
        if not Integer.check(value):
            return False        
        if 0 < value <= 65535:
            return True            
        return False

class Date(Email):
    '''
    Date
    -1 is indefinite in past
    0 is now
    +1 is indefinite in future
    '''
    NAME = 'ipport'
    _RE = re.compile('.*\:.*\:.*') #@todo (*1*) better regex
    
    @staticmethod
    def get_default():
        return "-1"

    @staticmethod
    def check(value):
        '''
        Check whether provided value is a valid tel nr
        '''
        if not String.check(value):
            return False
        value=Date.clean(value)
        return Date._RE.fullmatch(value) is not None

    @staticmethod
    def clean(v):
        if v==-1:
            v="-1"
        elif v==1:
            v="+1"
        elif v==0:
            v=="0"
        elif not String.check(v):
            raise ValueError("Input needs to be string:%s"%v)
        return v


class Duration(Email):
    '''
    Duration type

    Understood formats:
    - #w week
    - #d days
    - #h hours
    - #m minutes
    - #s seconds

    e.g. 10d is 10 days
    if int then in seconds

    -1 is infinite

    '''
    NAME = 'duration'
    _RE = re.compile('^(\d+)([wdhms]?)$')

    @staticmethod
    def check(value):
        if isinstance(value, int):
            if value == -1:
                return True
            elif value >= 0:
                return True
        elif isinstance(value, str):
            if DURATION_RE.fullmatch(value):
                return True
        return False

    @staticmethod
    def convertToSeconds(value):
        """Translate a string representation of a duration to an int
        representing the amount of seconds.

        Understood formats:
        - #w week
        - #d days
        - #h hours
        - #m minutes
        - #s seconds

        @param value: number or string representation of a duration in the above format
        @type value: string or int
        @return: amount of seconds
        @rtype: int
        """
        if not isinstance(value, str):
            return value
        m = DURATION_RE.matchall(value)
        if m:
            # Ok, valid format
            amount, granularity = m.groups()
            amount = int(amount)
            if granularity == 'w':
                multiplier = 60*60*24*7
            elif granularity == 'd':
                multiplier = 60*60*24
            elif granularity == 'h':
                multiplier = 60*60
            elif granularity == 'm':
                multiplier = 60
            elif granularity == 's':
                multiplier = 1
            else:
                # Default to seconds
                multiplier = 1
            return amount * multiplier
        return value



# class DirPath(Path):
#     '''Generic folder path type'''
#     NAME = 'dirpath'

#     @staticmethod
#     def check(value):
#         '''Check whether provided value is a valid directory path

#         This checks whether value is a valid Path only.
#         '''
#         return Path.check(value)

# class FilePath(Path):
#     '''Generic file path type'''
#     NAME = 'filepath'

#     @staticmethod
#     def check(value):
#         '''Check whether provided value is a valid file path

#         This checks whether value is a valid Path only.
#         '''
#         return Path.check(value)

# class UnixDirPath(DirPath):
#     '''Generic Unix folder path type'''
#     NAME = 'unixdirpath'

#     @staticmethod
#     def check(value):
#         '''Check whether provided value is a valid UNIX directory path

#         This checks whether value is a valid DirPath which starts and stops
#         with '/'.
#         '''
#         if not DirPath.check(value):
#             return False
#         return value.startswith("/") and value.endswith("/")

# class UnixFilePath(FilePath):
#     '''Generic Unix file path type'''
#     NAME = 'unixfilepath'

#     @staticmethod
#     def check(value):
#         '''Check whether provided value is a valid UNIX file path

#         This checks whether value is a valid FilePath which starts with '/' and
#         does not end with '/'.
#         '''
#         if not FilePath.check(value):
#             return False
#         return value.startswith("/") and not value.endswith("/")

# WINDOWS_DIR_RE = re.compile('^([a-zA-Z]:)?[\\\\/]')
# class WindowsDirPath(DirPath):
#     '''Generic Windows folder path type'''
#     NAME = 'windowsdirpath'

#     @staticmethod
#     def check(value):
#         '''Check whether provided value is a valid Windows directory path

#         This checks whether value is a valid DirPath which starts with '/' or
#         '\\', optionally prepended with a drive name, and ends with '/' or
#         '\\'.
#         '''
#         if not DirPath.check(value):
#             return False

#         if not WINDOWS_DIR_RE.match(value):
#             return False
#         return value.endswith(('\\', '/', ))

# WINDOWS_FILE_RE = re.compile('^([a-zA-Z]:)?[\\\\/]')
# class WindowsFilePath(FilePath):
#     '''Generic Windows file path type'''
#     NAME = 'windowsfilepath'

#     @staticmethod
#     def check(value):
#         '''Check whether provided value is a valid Windows file path

#         This checks whether value is a valid FilePath which starts with '/' or
#         '\\', optionally prepended with a drive name, and not ends with '/' or
#         '\\'.
#         '''
#         if not FilePath.check(value):
#             return False

#         if not WINDOWS_FILE_RE.match(value):
#             return False
#         return not value.endswith(('\\', '/', ))

