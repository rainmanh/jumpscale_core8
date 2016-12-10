from JumpScale import j

import brotli
import hashlib
import binascii
import pwd
import grp
from stat import *
import functools
import subprocess
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

    def _valid(self, fpath, excludes):
        """
        check if full path is in excludes
        """
        fpath = fpath.lower()
        for ex in excludes:
            if ex.match(fpath):
                return False
        return True

    def path2key(self, fpath):
        """
        @param fpath is full path
        """
        if not fpath.startswith(self.rootpath):
            raise j.exceptions.Input(message="fpath:%s needs to start with rootpath:%s" %
                                     (fpath, self.rootpath), level=1, source="", tags="", msgpub="")
        relPath = fpath[len(self.rootpath):].strip("/")
        toHash = self.namespace + relPath
        bl = pyblake2.blake2b(toHash.encode(), 32)
        binhash = bl.digest()
        return relPath, binascii.hexlify(binhash).decode()

    def add(self, path, excludes=[".*\.pyc", ".*__pycache__", ".*\.bak"]):
        """
        walk over path and put in plist
        @param excludes are regex expressions
        """

        if not j.sal.fs.exists(self.rootpath, followlinks=True):
            raise j.exceptions.Input(message="Rootpath: '%s' needs to exist" %
                                     self.rootpath, level=1, source="", tags="", msgpub="")

        # compiling regex for exclusion
        _excludes = []
        for ex in excludes:
            _excludes.append(re.compile(ex))

        if not j.sal.fs.exists(path, followlinks=True):
            if j.sal.fs.exists(j.sal.fs.joinPaths(self.rootpath, path), followlinks=True):
                path = j.sal.fs.joinPaths(self.rootpath, path)

        if not j.sal.fs.exists(path, followlinks=True):
            raise j.exceptions.Input(message="Could not find path:%s" % path, level=1, source="", tags="", msgpub="")

        # topdown=False means we do the lowest level dirs first
        for dirpath, dirs, files in os.walk(path, followlinks=True, topdown=False):

            if self._valid(dirpath, _excludes):

                relPath, dirkey = self.path2key(dirpath)
                ddir = self.dirCollection.get(dirkey, autoCreate=True)

                if ddir.dbobj.location == "":
                    ddir.dbobj.location = relPath
                else:
                    if ddir.location != relPath:
                        raise RuntimeError("serious bug, location should always be same")

                # sec base properties of current dirobj
                statCurDir = os.stat(dirpath, follow_symlinks=True)
                self._setMetadata(ddir.dbobj, statCurDir, dirpath)

                # now we have our core object, from db or is new
                ffiles = []
                llinks = []
                sspecials = []
                for fname in files:
                    fullpath = os.path.join(dirpath, fname)

                    # exclusion checking
                    if self._valid(fullpath, _excludes):

                        stat = os.stat(fullpath, follow_symlinks=False)
                        st_mode = stat.st_mode

                        if S_ISLNK(st_mode):
                            destlink = os.readlink(fullpath)
                            if not destlink.startswith(self.rootpath):  # check if is link & if outside of FS
                                ffiles.append((fullpath, stat))  # are links which point to outside of fs
                            else:
                                llinks.append((fullpath, stat, destlink))
                        else:
                            if S_ISREG(st_mode):
                                ffiles.append((fullpath, stat))
                            else:
                                sspecials.append((fullpath, stat))

                # initialize right amount of objects in capnp
                ddir.initNewSubObj("files", len(ffiles))
                ddir.initNewSubObj("links", len(llinks))
                ddir.initNewSubObj("specials", len(sspecials))

                # process files
                counter = 0
                for fullpathSub, stat in ffiles:
                    dbobj = ddir.dbobj.files[counter]
                    self._setMetadata(dbobj, stat, fullpathSub)
                    counter += 1

                # process links
                counter = 0
                for fullpathSub, stat, destlink in llinks:
                    obj = ddir.dbobj.files[counter]
                    relPath, dirkey = self.path2key(destlink)
                    obj.destDirKey = dirkey  # link to other directory
                    obj.destname = j.sal.fs.getBaseName(destlink)
                    self._setMetadata(obj, stat, fullpathSub)
                    counter += 1

                # process special files
                counter = 0
                for fullpathSub, stat, destlink in llinks:
                    obj = ddir.dbobj.files[counter]
                    # testing special files type
                    if S_ISSOCK(stat.st_mode):
                        obj.type = "socket"
                    elif S_ISBLK(stat.st_mode):
                        obj.type = "block"
                    elif S_ISCHR(stat.st_mode):
                        obj.type = "chardev"
                    elif S_ISFIFO(stat.st_mode):
                        obj.type = "fifopipe"
                    else:
                        obj.type = "unknown"
                    if S_ISBLK(stat.st_mode) or S_ISCHR(stat.st_mode):
                        id = '%d,%d' % (os.major(stat.st_rdev), os.minor(stat.st_rdev))
                        obj.data = id
                    self._setMetadata(obj, stat, fullpathSub)
                    counter += 1

                # filter the dirs based on the exclusions
                dirs = [os.path.join(dirpath, item)
                        for item in dirs if self._valid(os.path.join(dirpath, item), _excludes)]

                ddir.initNewSubObj("dirs", len(dirs))

                counter = 0
                for dir_sub_name in dirs:
                    dir_sub_path = os.path.join(dirpath, dir_sub_name)
                    dir_sub_obj = ddir.dbobj.dirs[counter]
                    counter += 1

                    dir_sub_relpath, dir_sub_key = self.path2key(dir_sub_path)
                    dir_sub_obj.key = dir_sub_key  # link to directory
                    dir_sub_obj.name = dir_sub_name

                    # needs to exist because of way how we walk (lowest to upper)
                    dir_obj = self.dirCollection.get(dir_sub_key, autoCreate=False)
                    dir_obj.setParent(ddir)
                    dir_obj.save()

                print("#################################")
                print(ddir)
                ddir.save()

    def _setMetadata(self, dbobj, stat, fpath):
        dbobj.name = j.sal.fs.getBaseName(fpath)

        dbobj.modificationTime = stat.st_mtime
        dbobj.creationTime = stat.st_ctime

        uname = pwd.getpwuid(stat.st_uid).pw_name
        # uname_id = stat.st_uid

        gname = grp.getgrgid(stat.st_gid).gr_name

        aci = self.aciCollection.new()
        aci.dbobj.uname = uname
        aci.dbobj.gname = gname
        aci.dbobj.mode = stat.st_mode

        if self.aciCollection.exists(aci.key):
            aci2 = self.aciCollection.get(aci.key)
            id = aci2.id
        else:
            id = int(aci.key[0: 4], 16)
            while self.aciCollection.lookup(id) != None:  # means exists
                id += 1

            aci.dbobj.id = id
            aci.save()

        dbobj.aclkey = id

    def walk(self, dirFunction=None, fileFunction=None, specialFunction=None, linkFunction=None, currentDirKey=""):
        """
        the function are taking following arguments:

        def dirFunction(dirobj, ttype, name ,key):
            # if you want to save do, this will make sure it gets changed
            dirObj.changed=True

            if you return True, then  will recurse, otherwise not


        def fileFunction(dirobj, ttype, name,structAsBelow):

            struct Link{
                name @0 : Text;
                aclkey @1: UInt32; #is pointer to ACL
                destDirKey @2: Text; #key of dir in which destination is
                destName @3: Text;
                modificationTime @4: UInt32;
                creationTime @5: UInt32;
            }

            # if you want to save do, this will make sure it gets changed
            dirObj.changed=True


        def linkFunction(dirobj, ttype, name,structAsBelow):

              struct Link{
                  name @0 : Text;
                  aclkey @1: UInt32; #is pointer to ACL
                  destDirKey @2: Text; #key of dir in which destination is
                  destName @3: Text;
                  modificationTime @4: UInt32;
                  creationTime @5: UInt32;
              }

            # if you want to save do, this will make sure it gets changed
            dirObj.changed=True


        def specialFunction(dirobj, ttype, name,structAsBelow):

              struct Special{
                  name @0 : Text;
                  type @1 :State;
                  # - 0: socket       (S_IFSOCK)
                  # - 1: block device (S_IFBLK)
                  # - 2: char. device (S_IFCHR)
                  # - 3: fifo pipe    (S_IFIFO)
                  enum State {
                    socket @0;
                    block @1;
                    chardev @2;
                    fifopipe @3;
                    unknown @4;
                  }
                  # data relevant for type of item
                  data @2 :Data;
                  modificationTime @3: UInt32;
                  creationTime @4: UInt32;
              }

            # if you want to save do, this will make sure it gets changed
            dirObj.changed=True



        """
        if currentDirKey == "":
            relkey, currentDirKey = self.path2key(self.rootpath)
        ddir = self.dirCollection.get(currentDirKey)

        for item in ddir.dbobj.dirs:
            recurse = dirFunction(ddir.dbobj, item.name, "D", item.key)
            if recurse:
                self.walk(dirFunction=dirFunction, fileFunction=fileFunction, specialFunction=specialFunction,
                          linkFunction=linkFunction, currentDirKey=ddir.key)

        for item in ddir.dbobj.files:
            dirFunction(ddir.dbobj, item.name, "F", item)

        for item in ddir.dbobj.links:
            dirFunction(ddir.dbobj, item.name, "L", item)

        for item in ddir.dbobj.specials:
            dirFunction(ddir.dbobj, item.name, "S", item)

    def dumps(self, trim=''):
        data = []

        def pprint(dirobj, ttype, name, *args):
            print("%s/%s (%s)" % (dirobj.location, name, ttype))

        self.walk(pprint, pprint, pprint, pprint)

        from IPython import embed
        print("DEBUG NOW in dumps")
        embed()
        raise RuntimeError("stop debug here")

        for f in self._data:
            p = f[0]
            if p.startswith(trim):
                p = p[len(trim):]

            line = "%s|%s|%d|%s|%s|%s|%d|%d|%d|%s" % (
                p, f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9]
            )
            data.append(line)

        return "\n".join(data) + "\n"

    def destroy(self):
        self.aciCollection.destroy()
        self.userGroupCollection.destroy()
        self.dirCollection.destroy()
