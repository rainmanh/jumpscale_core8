from JumpScale import j
import pyblake2
import binascii
import os
import calendar
import time


class FListMetadata:
    """Metadata layer on top of flist that enables flist manipulation"""
    def __init__(self, namespace="main", rootpath="/", dirCollection=None, aciCollection=None, userGroupCollection=None):
        self.namespace = namespace
        self.dirCollection = dirCollection
        self.aciCollection = aciCollection
        self.userGroupCollection = userGroupCollection
        self.rootpath = rootpath

    def get_fs(self, root_path="/"):
        raise NotImplementedError

    def delete(self, path):
        fType, dirObj = self._search_db(path)
        if fType == "D":
            dirObj.dbobj.state = "Deleted"
        else:
            _, entityList = self._getPropertyList(dirObj.dbobj, fType)
            for entity in entityList:
                if entity.name == j.sal.fs.getBaseName(path):
                    entity.state = "Deleted"
        dirObj.save()

    def stat(self, path):
        fType, dirObj = self._search_db(path)
        stat = {}

        if dirObj.dbobj.state != "":
            raise RuntimeError("%s: No such file or directory" % path)

        if fType == "D":
            stat["modificationTime"] = dirObj.dbobj.modificationTime
            stat["size"] = dirObj.dbobj.size
            stat["creationTime"] = dirObj.dbobj.creationTime
        else:
            _, entityList = self._getPropertyList(dirObj.dbobj, fType)
            for entity in entityList:
                if entity.name == j.sal.fs.getBaseName(path):
                    stat["modificationTime"] = entity.modificationTime
                    stat["size"] = entity.size
                    stat["creationTime"] = entity.creationTime
                    stat["blocksize"] = entity.blocksize
        return stat

    def move(self, old_path, new_parent_path, fname=""):
        """
        Move/Rename files or directories
        :param old_path: path of files/dirs to be moved
        :param new_parent_path: path of the new parent directory
        :param fname: file name if desired to rename the entity

        Examples:
        ## Move directory:
        flistmeta.move("/tmp/dir/subdir", "/tmp/dir/subdir2")
        ## Rename directory
        flistmeta.move("/tmp/dir/subdir", "/tmp/dir/subdir", "subdir3")
        ## Move file
        flistmeta.move("/tmp/dir/subdir/sample.txt", "/tmp/dir/subdir2")
        ## Rename file
        flistmeta.move("/tmp/dir/subdir/sample.txt", "/tmp/dir/subdir", "sample2.txt")
        """
        oldFtype, oldDirObj = self._search_db(old_path)
        newFtype, newParentDirObj = self._search_db(new_parent_path)
        oldFName = j.sal.fs.getBaseName(old_path)
        fname = fname if fname else oldFName

        if oldFtype == "D":
            if "{}/".format(old_path) in new_parent_path:
                raise RuntimeError("Cannot move '{}' to a subdirectory of itself, '{}'".format(old_path, new_parent_path))

            if oldDirObj.dbobj.state != "":
                raise RuntimeError("%s: No such file or directory" % old_path)

            _, parentDir = self._search_db(j.sal.fs.getDirName(old_path))
            self._move_dir(parentDir, newParentDirObj, oldDirObj, fname=fname)
        else:
            self._move_file(oldDirObj, newParentDirObj, oldFName, fname, oldFtype)

    def _move_dir(self, parentDir, newParentDirObj, dirObj, fname):
        if parentDir.key != newParentDirObj.key:
            dirProps = self._removeObj(parentDir, dirObj.dbobj.name, "D")
            dirProps["name"] = fname
            self._addObj(newParentDirObj, dirProps, "D")
            dirObj.dbobj.location = os.path.join(newParentDirObj.dbobj.location, fname)
            dirObj.dbobj.name = fname
            dirObj.dbobj.parent = newParentDirObj.key

            _, dirKey = self._path2key(os.path.join(self.rootpath, newParentDirObj.dbobj.location, fname))
            ddir = self.dirCollection.get(dirKey, autoCreate=True)
            ddir.dbobj = dirObj.dbobj
            ddir.save()
            dirObj.dbobj.state = "Moved"
        elif dirObj.dbobj.name != fname:  # Rename only
            for dir in parentDir.dbobj.dirs:
                if dir.name != dirObj.dbobj.name:
                    dir.name = fname
            dirObj.dbobj.location = os.path.join(newParentDirObj.dbobj.location, fname)
            dirObj.dbobj.name = fname
            # Save new dir object
            _, dirKey = self._path2key(self.rootpath, os.path.join(newParentDirObj.dbobj.location, fname))
            ddir = self.dirCollection.get(dirKey, autoCreate=True)
            ddir.dbobj = dirObj.dbobj
            ddir.save()
            dirObj.dbobj.state = "Moved"
        parentDir.save()
        newParentDirObj.save()
        dirObj.save()

    def _move_file(self, parentDir, newParentDirObj, oldFName, fname, ftype):
        if parentDir.key != newParentDirObj.key:
            fileProps = self._removeObj(parentDir, oldFName, ftype)
            fileProps["name"] = fname
            self._addObj(newParentDirObj, fileProps, ftype)
        elif oldFName != fname:
            for file in parentDir.dbobj.files:
                if oldFName != fname:
                    file.name = fname
                    file.modificationTime = calendar.timegm(time.gmtime())
        parentDir.save()
        newParentDirObj.save()

    def _removeObj(self, dirObj, name, ptype):
        newFiles = []
        poppedFile = {}
        pName, pList = self._getPropertyList(dirObj.dbobj, ptype)
        for index, file in enumerate(pList):
            if file.name == name:
                poppedFile = file.to_dict()
            else:
                newFiles.append(file.to_dict())

        newlist = dirObj.dbobj.init(pName, len(newFiles))
        for i, item in enumerate(newFiles):
            newlist[i] = item
        return poppedFile

    def _addObj(self, dirObj, fileProps, ptype):
        pName, pList = self._getPropertyList(dirObj.dbobj, ptype)
        newFiles = [item.to_dict() for item in pList]
        newFiles.append(fileProps)
        newlist = dirObj.dbobj.init(pName, len(newFiles))
        for i, item in enumerate(newFiles):
            newlist[i] = item

    def _getPropertyList(self, dbobj, ptype):
        if ptype == "D":
            return "dirs", dbobj.dirs
        if ptype == "F":
            return "files", dbobj.files
        if ptype == "L":
            return "links", dbobj.links
        if ptype == "S":
            return "specials", dbobj.specials

    def _search_db(self, ppath):
        """
        Search for file or directory through the database
        @return if ppath is file then it'll return directory containing the file
                else it'll return the dir
        """
        absolutePath = self._get_absolute_path(ppath)
        try:
            return "D", self._get_dir_from_db(absolutePath)
        except:
            # Means that ppath is a file or doesn't exist
            baseName = j.sal.fs.getBaseName(absolutePath)
            parent_dir = j.sal.fs.getDirName(absolutePath)
            parent_dir_obj = self._get_dir_from_db(parent_dir)

            # Search for file in parent_dir
            for index, file in enumerate(parent_dir_obj.dbobj.files):
                if file.name == baseName:
                    return "F", parent_dir_obj

            # Search for links
            for index, link in enumerate(parent_dir_obj.dbobj.links):
                if link.name == baseName:
                    return "L", parent_dir_obj

            # Search for links
            for index, special in enumerate(parent_dir_obj.dbobj.specials):
                if special.name == baseName:
                    return "S", parent_dir_obj

            raise RuntimeError("%s: No such file or directory" % absolutePath)

    def _get_dir_from_db(self, dirPath):
        _, key = self._path2key(dirPath)
        return self.dirCollection.get(key)

    def _get_absolute_path(self, path):
        if path.startswith(self.rootpath):
            return os.path.join(self.rootpath, path)
        return path

    def _path2key(self, fpath):
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
