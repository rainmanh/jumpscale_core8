from JumpScale import j

import brotli
import hashlib
import binascii
import pwd
import grp
from stat import S_ISBLK, S_ISSOCK, S_ISCHR, S_ISFIFO, S_ISLNK, S_ISREG
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


class FList:
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

    def getDir(self, key):
        return self.dirCollection.get(key)

    def _loadDirProperties(self, dirKey, dirpathAbsolute, dirRelPath):
        """Load dir properties into DirCollection dbobj"""
        ddir = self.dirCollection.get(dirKey, autoCreate=True)
        if ddir.dbobj.location == "":
            ddir.dbobj.location = dirRelPath
        else:
            if ddir.location != dirRelPath:
                raise RuntimeError("serious bug, location should always be same")

        # sec base properties of current dirobj
        statCurDir = os.stat(dirpathAbsolute, follow_symlinks=True)
        dirname = j.sal.fs.getBaseName(dirpathAbsolute)
        self._setMetadata(ddir.dbobj, statCurDir, dirname)
        return ddir

    def add(self, path, excludes=[".*\.pyc", ".*__pycache__", ".*\.bak", ".*\.git"]):
        """
        walk over path and put in plist
        @param excludes are regex expressions and they start inside the rootpath !
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
        for dirpathAbsolute, dirs, files in os.walk(path, followlinks=True, topdown=False):

            # dirpath is full path need to bring it to the relative part
            dirRelPath, dirKey = self.path2key(dirpathAbsolute)
            print("%s||%s" % (dirpathAbsolute, dirKey))

            if self._valid(dirRelPath, _excludes):
                ddir = self._loadDirProperties(dirKey, dirpathAbsolute, dirRelPath)

                # now we have our core object, from db or is new
                ffiles = []
                llinks = []
                sspecials = []
                for fname in files:
                    relPathWithName = os.path.join(dirRelPath, fname)
                    pathAbsolute = os.path.join(self.rootpath, relPathWithName)

                    # exclusion checking
                    if self._valid(relPathWithName, _excludes):

                        stat = os.stat(pathAbsolute, follow_symlinks=False)
                        st_mode = stat.st_mode

                        if S_ISLNK(st_mode):
                            # print("LINK")
                            # Checking absolute path, relative may fail
                            destlink = os.path.realpath(pathAbsolute)
                            if not destlink.startswith(self.rootpath):  # check if is link & if outside of FS
                                # print("OUTSIDE")
                                ffiles.append((fname, stat))  # are links which point to outside of fs
                            else:
                                # print("INSIDE")
                                # Ensure relative path works
                                destlink = os.readlink(pathAbsolute)
                                llinks.append((fname, stat, destlink))
                        else:
                            if S_ISREG(st_mode):
                                # print("REGULAR")
                                ffiles.append((fname, stat))
                            else:
                                # print("SPECIAL")
                                sspecials.append((fname, stat))

                # initialize right amount of objects in capnp
                ddir.initNewSubObj("files", len(ffiles))
                ddir.initNewSubObj("links", len(llinks))
                ddir.initNewSubObj("specials", len(sspecials))
                # process files
                for index, (fname, stat) in enumerate(ffiles):
                    dbobj = ddir.dbobj.files[index]
                    self._setMetadata(dbobj, stat, fname)

                # process links
                for index, (fname, stat, destlink) in enumerate(llinks):
                    obj = ddir.dbobj.links[index]
                    # FIXME
                    # relPath, dirkey = self.path2key(destlink)
                    # obj.destDirKey = dirkey  # link to other directory
                    # obj.destname = j.sal.fs.getBaseName(destlink)
                    obj.destname = destlink
                    self._setMetadata(obj, stat, fname)

                # process special files
                for index, (fname, stat) in enumerate(sspecials):
                    obj = ddir.dbobj.specials[index]
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
                    self._setMetadata(obj, stat, fname)

                # filter the dirs based on the exclusions (starting from the relative paths)
                dirs2 = [os.path.join(dirRelPath, item)
                         for item in dirs if self._valid(os.path.join(dirRelPath, item), _excludes)]
                ddir.initNewSubObj("dirs", len(dirs2))

                for index, dirRelPathFull in enumerate(dirs2):
                    absDirPathFull = os.path.join(self.rootpath, dirRelPathFull)
                    dir_sub_obj = ddir.dbobj.dirs[index]

                    dir_sub_relpath, dir_sub_key = self.path2key(absDirPathFull)
                    print("%s|%s" % (absDirPathFull, dir_sub_key))
                    dir_sub_obj.key = dir_sub_key  # link to directory
                    dir_sub_obj.name = j.sal.fs.getBaseName(dirRelPathFull)

                    # needs to exist because of way how we walk (lowest to upper)
                    dir_obj = self.dirCollection.get(dir_sub_key, autoCreate=False)
                    dir_obj.setParent(ddir)
                    dir_obj.save()

                # print("#################################")
                # print(ddir)
                ddir.save()

    def _setMetadata(self, dbobj, stat, fname):
        dbobj.name = fname
        # j.sal.fs.getBaseName(fpath)

        dbobj.modificationTime = int(stat.st_mtime)
        dbobj.creationTime = int(stat.st_ctime)
        dbobj.size = stat.st_size

        uname = pwd.getpwuid(stat.st_uid).pw_name
        # uname_id = stat.st_uid

        gname = grp.getgrgid(stat.st_gid).gr_name

        aci = self.aciCollection.new()
        aci.dbobj.uname = uname
        aci.dbobj.gname = gname
        aci.dbobj.mode = stat.st_mode

        if not self.aciCollection.exists(aci.key):
            aci.save()

        dbobj.aclkey = aci.key

    def walk(self, dirFunction=None, fileFunction=None, specialFunction=None, linkFunction=None, args={}, currentDirKey="", dirRegex=[], fileRegex=[], types="DFLS"):
        """

        @param types: D=Dir, F=File, L=Links, S=Special

        the function are taking following arguments:

        def dirFunction(dirobj, ttype, name, args ,key):
            # if you want to save do, this will make sure it gets changed
            dirObj.changed=True

            if you return False, then it will not recurse, std behavior is to recurse

        def fileFunction(dirobj, ttype, name, args,subobj=structAsBelow):

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

        def linkFunction(dirobj, ttype, name, args,subobj=structAsBelow):

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

        def specialFunction(dirobj, ttype, name, args,subobj=structAsBelow):

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

        def valid(fpath, includes):
            """
            check if full path is in includes
            """
            if includes == []:
                return True
            fpath = fpath.lower()
            for ex in includes:
                if ex.match(fpath):
                    return True
            return False

        if j.data.types.string.check(dirRegex):
            if dirRegex.strip() == "":
                dirRegex = []
            else:
                dirRegex = [dirRegex]

        if j.data.types.string.check(fileRegex):
            if fileRegex.strip() == "":
                fileRegex = []
            else:
                fileRegex = [fileRegex]

        # precompile the regexes (faster)
        dirRegex = [re.compile(ex) for ex in dirRegex]
        fileRegex = [re.compile(ex) for ex in fileRegex]

        if currentDirKey == "":
            relkey, currentDirKey = self.path2key(self.rootpath)

        ddir = self.dirCollection.get(currentDirKey)

        for item in ddir.dbobj.dirs:
            if valid(j.sal.fs.joinPaths(ddir.dbobj.location, item.name), dirRegex) and "D" in types:
                recurse = dirFunction(dirobj=ddir, type="D", name=item.name, args=args,
                                      key=item.key)
            else:
                recurse = True
            if recurse is not False:
                if item.key == "":
                    raise RuntimeError("key cannot be empty in a subdir of: ddir\n%s" % ddir)
                self.walk(dirFunction=dirFunction,
                          fileFunction=fileFunction,
                          specialFunction=specialFunction,
                          linkFunction=linkFunction,
                          args=args,
                          currentDirKey=item.key,
                          dirRegex=dirRegex,
                          fileRegex=fileRegex,
                          types=types)

        if not valid(ddir.dbobj.location, dirRegex):
            return

        for item in ddir.dbobj.files:
            # print(item)
            if valid(j.sal.fs.joinPaths(ddir.dbobj.location, item.name), fileRegex) and "F" in types:
                fileFunction(dirobj=ddir, type="F", name=item.name, subobj=item, args=args)

        for item in ddir.dbobj.links:
            # print(item)
            if valid(j.sal.fs.joinPaths(ddir.dbobj.location, item.name), fileRegex) and "L" in types:
                linkFunction(dirobj=ddir, type="L", name=item.name, subobj=item, args=args)

        for item in ddir.dbobj.specials:
            # print(item)
            if valid(j.sal.fs.joinPaths(ddir.dbobj.location, item.name), fileRegex and "S" in types):
                specialFunction(dirobj=ddir, type="S", name=item.name, subobj=item, args=args)

    def count(self, dirRegex=[], fileRegex=[], types="DFLS"):
        """
        @regex can be str or list of regex:[]
        @return size,nrfiles,nrdirs,nrlinks,nrspecial
        """

        def procDir(dirobj, type, name, args, key):
            args["nrdirs"] += 1

        def procFile(dirobj, type, name, subobj, args):
            args["size"] += subobj.size
            args["nrfiles"] += 1

        def procLink(dirobj, type, name, subobj, args):
            args["nrlinks"] += 1

        def procSpecial(dirobj, type, name, subobj, args):
            args["nrspecial"] += 1

        result = {}
        result["size"] = 0
        result["nrfiles"] = 0
        result["nrlinks"] = 0
        result["nrdirs"] = 0
        result["nrspecial"] = 0
        self.walk(
            dirFunction=procDir,
            fileFunction=procFile,
            specialFunction=procSpecial,
            linkFunction=procLink,
            args=result,
            dirRegex=dirRegex,
            fileRegex=fileRegex,
            types=types
        )

        return (result["size"], result["nrfiles"], result["nrdirs"], result["nrlinks"], result["nrspecial"])

    def pprint(self, dirRegex=[], fileRegex=[], types="DFLS"):

        def procDir(dirobj, type, name, args, key):
            print("%s/%s (%s)" % (dirobj.dbobj.location, name, type))

        def procFile(dirobj, type, name, subobj, args):
            print("%s/%s (%s)" % (dirobj.dbobj.location, name, type))

        def procLink(dirobj, type, name, subobj, args):
            print("%s/%s (%s)" % (dirobj.dbobj.location, name, type))

        def procSpecial(dirobj, type, name, subobj, args):
            print("%s/%s (%s)" % (dirobj.dbobj.location, name, type))

        result = []
        self.walk(
            dirFunction=procDir,
            fileFunction=procFile,
            specialFunction=procSpecial,
            linkFunction=procLink,
            args=result,
            dirRegex=dirRegex,
            fileRegex=fileRegex,
            types=types
        )

    def dumps(self, dirRegex=[], fileRegex=[], types="DFLS"):
        """
        dump to text based flist format
        """

        # Set common values for all types
        # Others fields (type, hash, extended) need to be filled by caller
        def setDefault(dirobj, name, subobj):
            x = self.aciCollection.get(subobj.aclkey)
            item = [
                "%s/%s" % (dirobj.dbobj.location, name),  # Path
                "", # To be filled lated                  # Hash
                "%d" % subobj.size,                       # Size
                x.dbobj.uname,                            # User (permissions)
                x.dbobj.gname,                            # Group (permissions)
                x.modeInOctFormat,                        # Permission mode
                "", # To be filled later                  # File type
                "%d" % subobj.creationTime,               # Creation Timestamp
                "%d" % subobj.modificationTime,           # Modification Timestamp
                ""  # To be filled later                  # Extended attributes
            ]
            return item

        def procDir(dirobj, type, name, args, key):
            item = setDefault(dirobj, name, dirobj.dbobj)

            # Set types (directory)
            item[6] = "4"

            args.append("|".join(item))

        def procFile(dirobj, type, name, subobj, args):
            item = setDefault(dirobj, name, subobj)

            # Set filetype
            fullpath = "%s/%s/%s" % (self.rootpath, dirobj.dbobj.location, name)
            item[1] = j.data.hash.md5(fullpath)
            item[6] = "2"

            args.append("|".join(item))

        def procLink(dirobj, type, name, subobj, args):
            item = setDefault(dirobj, name, subobj)

            # Set filetype
            item[6] = "1"
            item[9] = subobj.destname

            args.append("|".join(item))

        def procSpecial(dirobj, type, name, subobj, args):
            print("============== SPECIAL (not implemented yet)")
            print(subobj)

            print("%s/%s (%s)" % (dirobj.dbobj.location, name, type))
            print("==============")

        print("Building old flist format")
        result = []
        self.walk(
            dirFunction=procDir,
            fileFunction=procFile,
            specialFunction=procSpecial,
            linkFunction=procLink,
            args=result
        )

        print(result)
        return "\n".join(result) + "\n"

        """
        from IPython import embed
        print("DEBUG NOW in dumps")
        embed()
        raise RuntimeError("stop debug here")

        for f in rawdata:
            p = f[0]
            if p.startswith(trim):
                p = p[len(trim):]

            line = "%s|%s|%d|%s|%s|%s|%d|%d|%d|%s" % (
                p, f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9]
            )
            data.append(line)

        return "\n".join(data) + "\n"
        """

    def destroy(self):
        self.aciCollection.destroy()
        self.userGroupCollection.destroy()
        self.dirCollection.destroy()
