from JumpScale import j
from stat import *
import pwd
import grp
import os
import sys

class FListFactory(object):
    def __init__(self):
        self.__jslocation__ = "j.tools.flist"

    def create(self):
        return FList()
        
    def load(self, flist):
        # ...
        return FList()
    
class FList(object):
    """
        FList (sometime "plist") files contains a plain/text representation of
    a complete file system tree
    
        FList stand for "file list" (plist for "path list"), this format is made
    for mapping a file with his md5 hash, which allow to retreive file remotly
    and get it's metadata separatly
    
        FList is formatted to support POSIX ACL, File type representation and
    extra data (can be any type but it's used internaly to describe some file-type)
        
        A flist file contains one entry per file, fields are separated by "|".
    Filename should not contains the pipe character in it's name otherwise it will
    not be supported at all.
    
        This is a flist file format supported by this library:
    filepath|hash|filesize|uname|gname|permissions|filetype|ctime|mtime|extended
    
        - filepath: the complete file path on the filesystem
        - hash: md5 checksum of the file
          - if the file is a special file (block, sylink, ...), use this hash:
            md5("flist:" + filename (fullpath) + ":" + mtime)
        - filesize: size in bytes

        - uname: username owner of the file (used for permissions)
          - note: if username doesn't match any userid, userid will be used
        - gname: groupname owner of the file (used for permissions)
          - note: if groupname doesn't match any groupid, groupid will be used

        - permissions: octal representation of the posix permissions
        - filetype: integer representing the file type:
          - 0: socket       (S_IFSOCK)
          - 1: symlink      (S_IFLNK)
          - 2: regular file (S_IFREG)
          - 3: block device (S_IFBLK)
          - 4: directory    (S_IFDIR) (this is not required)
          - 5: char. device (S_IFCHR)
          - 6: fifo pipe    (S_IFIFO)

        - ctime: unix timestamp of the creation time
        - mtime: unix timestamp of the modification file

        - extended: optional field which may contains extra-data related to
          to file type:
          - symlink     : contains the target of the link
          - block device: ...
          - char. device: ...

    """
    def __init__(self):
        self._data = []
        self._hash = {}
        self._path = {}
    
    def parse(self, filename):
        del self._data[:]
        self._hash.clear()
        self._path.clear()

        index = 0

        with open(filename) as flist:
            for line in flist:
                f = line.strip().split('|')
                
                index = self._indexForHash(f[1])
                
                self._data[index] = [
                    f[0],        # path
                    f[1],        # hash
                    int(f[2]),   # size
                    f[3],        # uname
                    f[4],        # gname
                    f[5],        # permission
                    int(f[6]),   # filetype
                    int(f[7]),   # ctime
                    int(f[8]),   # mtime
                    f[9]         # extended
                ]
        
        return index

    """
    Getters
    """
    def _indexFromHash(self, hash):
        if hash not in self._hash:
            return None

        return self._hash[hash]
    
    def getHashList(self):
        return list(self._hash.keys())

    def getObject(self, hash):
        object = {
            # ...
        }

        return object
    
    def _getItem(self, hash, index):
        id = self._hash[hash]
        if id is not None:
            return self._data[id][index]

        return None
        
    def getPath(self, hash):
        return self._getItem(hash, 0)

    def getType(self, hash):
        type = self._getItem(hash, 0)
        if type is None:
            return None
        
        # FIXME
        
        return None
    
    
    def isRegular(self, hash):
        return self._getItem(hash, 6) == 2


    def getSize(self, hash):
        return self._getItem(hash, 2)

    def getMode(self, hash):
        return self._getItem(hash, 5)

    def getOwner(self, hash):
        return self._getItem(hash, 3)

    def getGroup(self, hash):
        return self._getItem(hash, 4)

    def getExtended(self, hash):
        # return self._getItem(hash, 0)
        return -1

    def getCreationTime(self, hash):
        return self._getItem(hash, 7)

    def getModificationTime(self, hash):
        return self._getItem(hash, 8)

    """
    Setters
    """
    def _indexForHash(self, hash):
        if hash not in self._hash:
            # creating new entry
            self._data.append([None] * 10)
            id = len(self._data) - 1
            self._data[id][1] = hash
            self._hash[hash] = id

        return self._hash[hash]

    def _setItem(self, hash, value, index):
        id = self._indexForHash(hash)
        if id is None:
            return None
        
        self._data[id][index] = value
        return value
        
    def setPath(self, hash, value):
        return self._setItem(hash, value, 0)

    def setType(self, hash, value):
        # testing regular first, it will be
        # the most often used type (in theory)
        if S_ISREG(value):
            return self._setItem(hash, 2, 6)

        # testing special files type
        if S_ISSOCK(value):
            return self._setItem(hash, 0, 6)

        if S_ISLNK(value):
            return self._setItem(hash, 1, 6)

        if S_ISBLK(value):
            return self._setItem(hash, 3, 6)

        if S_ISCHR(value):
            return self._setItem(hash, 5, 6)

        if S_ISFIFO(value):
            return self._setItem(hash, 6, 6)
        
        # not necessary in flist, but keep if for portability
        if S_ISDIR(value):
            return self._setItem(hash, 4, 6)
        
        return None

    def setSize(self, hash, value):
        return self._setItem(hash, value, 2)

    def setMode(self, hash, value):
        return self._setItem(hash, value, 5)

    def setOwner(self, hash, value):
        return self._setItem(hash, value, 3)

    def setGroup(self, hash, value):
        return self._setItem(hash, value, 4)

    def setExtended(self, hash, value):
        """
        value: need to be a stat struct
        """
        path = self._getItem(hash, 0)
        
        # symlink
        if S_ISLNK(value.st_mode):
            xtd = os.readlink(path)
            return self._setItem(hash, xtd, 9)
        
        # block device
        if S_ISBLK(value.st_mode) or S_ISCHR(value.st_mode):
            id = '%d,%d' % (os.major(value.st_rdev), os.minor(value.st_rdev))
            return self._setItem(hash, id, 9)

        return self._setItem(hash, "", 9)

    def setModificationTime(self, hash, value):
        return self._setItem(hash, int(value), 7)

    def setCreationTime(self, hash, value):
        return self._setItem(hash, int(value), 8)
    
    """
    Builder
    """
    def _build(self, filename):
        stat = os.stat(filename, follow_symlinks=False)
        mode = oct(stat.st_mode)[4:]
        
        # grab username from userid, if not found, use userid
        try:
            uname = pwd.getpwuid(stat.st_uid).pw_name
        except:
            uname = stat.st_uid
        
        # grab groupname from groupid, if not found, use groupid
        try:
            gname = grp.getgrgid(stat.st_gid).gr_name
        except:
            gname = stat.st_gid
        
        # compute hash only if it's a regular file, otherwise, comute filename hash
        # the hash is used to access the file "id" in the list, we cannot have empty hash
        if not S_ISREG(stat.st_mode):
            hashstr = "flist:%s:%d" % (filename, stat.st_mtime)
            hash = j.data.hash.md5_string(hashstr)

        else:
            hash = j.data.hash.md5(filename)

        self.setPath(hash, filename)
        self.setType(hash, stat.st_mode)
        self.setSize(hash, stat.st_size)
        self.setMode(hash, mode)
        self.setOwner(hash, uname)
        self.setGroup(hash, gname)
        self.setExtended(hash, stat)
        self.setModificationTime(hash, stat.st_mtime)
        self.setCreationTime(hash, stat.st_ctime)

    def build(self, path, excludes=[]):
        if len(self._data) > 0:
            # this can be only done on empty list
            return None

        for dirpath, dirs, files in os.walk(path):
            skip = False

            for e in excludes:
                if dirpath.startswith(e):
                    skip = True

            if skip:
                continue

            for filename in files:
                fname = os.path.join(dirpath, filename)
                self._build(fname)

        return len(self._data)

    """
    Exporting
    """
    def dumps(self):
        data = []
        
        for f in self._data:
            line = "%s|%s|%d|%s|%s|%s|%d|%d|%d|%s" % (
                f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9]
            )
            data.append(line)
            
        return "\n".join(data) + "\n"
    
    def _debug(self):
        tableMain = sys.getsizeof(self._data)
        tableHash = sys.getsizeof(self._hash)
        tablePath = sys.getsizeof(self._path)
        
        print("Main table: %.2f ko" % (float(tableMain) / 1024))
        print("Hash table: %.2f ko" % (float(tableHash) / 1024))
        print("Path table: %.2f ko" % (float(tablePath) / 1024))

