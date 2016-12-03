from JumpScale import j
from stat import *
import brotli
import hashlib
import functools
import subprocess
import pwd
import grp
import os
import sys
import re
import pyblake2
import capnp
from JumpScale.tools.flist import model_capnp as ModelCapnp

from JumpScale.tools.flist.models import DirModel
from JumpScale.tools.flist.models import DirCollection

from path import Path


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
            md5("flist:" + fpath (fullpath) + ":" + mtime)
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
          - 4: directory    (S_IFDIR) (used for empty directory)
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

    def __init__(self, namespace="main", rootpath="", dirCollection=None, aciCollection=None, userGroupCollection=None):
        self.namespace = namespace
        self.dirCollection = dirCollection
        self.aciCollection = aciCollection
        self.userGroupCollection = userGroupCollection
        self.rootpath = rootpath
        if not j.sal.fs.exists(self.rootpath, followlinks=True):
            raise j.exceptions.Input(message="Rootpath: '%s' needs to exist" %
                                     self.rootpath, level=1, source="", tags="", msgpub="")

    def __valid(self, fpath, excludes):
        """
        check if full path is in excludes
        """
        for ex in excludes:
            if ex.match(fpath):
                return False

        return True

    def add(self, path, excludes=[".pyc", "__pycache__", ".bak"]):
        """
        walk over path and put in plist
        @param excludes are regex expressions
        """

        # compiling regex for exclusion
        __excludes = []
        for ex in excludes:
            __excludes.append(re.compile(ex))

        for dirpath, dirs, files in os.walk(path, followlinks=True):

            if self.__valid(dirpath, __excludes):

                relPath = j.sal.fs.pathRemoveDirPart(dirpath, self.rootpath, True)
                toHash = self.namespace + relPath
                bl = pyblake2.blake2b(toHash.encode(), 32)
                binhash = bl.digest()

                ddir = self.dirCollection.get(binhash, autoCreate=True)

                if ddir.dbobj.location == "":
                    print("NEW DIR:%s" % relPath)
                    new = True
                    ddir.location = relPath
                else:
                    new = False
                    if ddir.location != relPath:
                        raise RuntimeError("serious bug, location should always be same")

                # now we have our core object, from db or is new

                for fpath in files:
                    fpath = os.path.join(dirpath, fpath)

                    # exclusion checking
                    if not self.__valid(fpath, __excludes):
                        continue

                    ddir.addPath(fpath)
                    from IPython import embed
                    print("DEBUG NOW ooo")
                    embed()
                    raise RuntimeError("stop debug here")

                for dpathRel in dirs:
                    dirpath2 = os.path.join(dirpath, dpathRel)
                    relPath = j.sal.fs.pathRemoveDirPart(dirpath2, self.rootpath, True)

                    toHash = self.namespace + relPath
                    bl = pyblake2.blake2b(toHash.encode(), 32)
                    binhash = bl.digest()

                    ddir2 = self.dirCollection.get(binhash, autoCreate=True)

                    if ddir2.dbobj.location == "":
                        print("NEW SUBDIR:%s" % relPath)
                        ddir2.location = relPath
                    else:
                        if ddir2.location != relPath:
                            raise RuntimeError("serious bug, location should always be same")

                    ddir2.setParent(ddir)
                    ddir2.save()

                    ddir.addDir(ddir2)

                ddir.save()

    """
    Exporting
    """

    def dumps(self, trim=''):
        data = []

        for f in self._data:
            p = f[0]
            if p.startswith(trim):
                p = p[len(trim):]

            line = "%s|%s|%d|%s|%s|%s|%d|%d|%d|%s" % (
                p, f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9]
            )
            data.append(line)

        return "\n".join(data) + "\n"
