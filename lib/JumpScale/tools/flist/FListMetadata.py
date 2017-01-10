from JumpScale import j
import pyblake2
import binascii
import os


class FListMetadata:
    """Metadata layer on top of flist that enables flist manipulation"""
    def __init__(self, namespace="main", rootpath="/", dirCollection=None, aciCollection=None, userGroupCollection=None):
        self.namespace = namespace
        self.dirCollection = dirCollection
        self.aciCollection = aciCollection
        self.userGroupCollection = userGroupCollection
        self.rootpath = rootpath

    def create(self, parent_path, name, mode=""):
        raise NotImplementedError

    def mkdir(self, parent_path, name, mode=""):
        raise NotImplementedError

    def delete(self, path):
        raise NotImplementedError

    def chmod(self, path, mode=""):
        raise NotImplementedError

    def move(self, old_path, new_parent_path, fname=""):
        oldFtype, oldDirObj = self._search_db(old_path)
        newFtype, newParentDirObj = self._search_db(new_parent_path)
        fname = fname if fname else j.sal.fs.getBaseName(old_path)

        if oldFtype == "D":
            if old_path in new_parent_path:
                raise RuntimeError("Cannot move '{}' to a subdirectory of itself, '{}'".format(old_path, new_parent_path))
            _, parentDir = self._search_db(j.sal.fs.getDirName(old_path))
            self._move_dir(parentDir, newParentDirObj, oldDirObj, fname=fname)

    def _move_dir(self, parentDir, newParentDirObj, dirObj, fname):
        if parentDir.key != newParentDirObj.key:
            dirProps = self._removeDirObj(parentDir, dirObj.dbobj.name)
            dirProps["name"] = fname
            self._addDirObj(newParentDirObj, dirProps)
            dirObj.dbobj.location = os.path.join(newParentDirObj.dbobj.location, fname)
            dirObj.dbobj.name = fname
        elif dirObj.dbobj.name != fname:  # Rename only
            for dir in parentDir.dbobj.dirs:
                if dir.name == dirObj.dbobj.name:
                    dir.name = fname
            dirObj.dbobj.location = os.path.join(newParentDirObj.dbobj.location, fname)
            dirObj.dbobj.name = fname

    def _removeDirObj(self, dirObj, name):
        newDirs = []
        poppedDir = {}
        for index, dir in enumerate(dirObj.dbobj.dirs):
            if dir.name == name:
                poppedDir = dir.to_dict()
            else:
                newDirs.append(dir.to_dict())

        newlist = dirObj.dbobj.init("dirs", len(newDirs))
        for i, item in enumerate(newDirs):
            newlist[i] = item

        return poppedDir

    def _addDirObj(self, dirObj, dirProps):
        newDirs = [item.to_dict() for item in dirObj.dbobj.dirs]
        newDirs.append(dirProps)
        newlist = dirObj.dbobj.init("dirs", len(newDirs))
        for i, item in enumerate(newDirs):
            newlist[i] = item

    def get_fs(self, root_path="/"):
        raise NotImplemented

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
