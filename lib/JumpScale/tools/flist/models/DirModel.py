
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class DirModel(base):
    """
    Model Class for an Issue object
    """

    def index(self):
        # put indexes in db as specified
        #@TODO: *1 needs to be implemented
        from IPython import embed
        print("DEBUG NOW index")
        embed()
        raise RuntimeError("stop debug here")
        ind = "%s:%s" % (self.dbobj.name, self.dbobj.state)
        self._index.index({ind: self.key})

    def addDir(self, dirObject):
        from IPython import embed
        print("DEBUG NOW dirpath")
        embed()
        raise RuntimeError("stop debug here")

    def addPath(self, fpath):
        """
        build 1 entry for the plist with full path
        """

        from IPython import embed
        print("DEBUG NOW addPath")
        embed()
        raise RuntimeError("stop debug here")

        stat = os.stat(fpath, follow_symlinks=False)
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

        # compute hash only if it's a regular file, otherwise, comute fpath hash
        # the hash is used to access the file "id" in the list, we cannot have empty hash
        if S_ISREG(stat.st_mode):
            #     hashstr = "flist:%s:%d" % (fpath, stat.st_mtime)
            #     hash = j.data.hash.md5_string(hashstr)
            #
            # else:
            self.hash = j.data.hash.md5(fpath)

        # testing regular first, it will probably be
        # the most often used type
        value = stat.st_mode
        if S_ISREG(value):
            self.data[6] = 2

        # testing special files type
        elif S_ISSOCK(value):
            self.data[6] = 0

        elif S_ISLNK(value):
            self.data[6] = 1

        elif S_ISBLK(value):
            self.data[6] = 3

        elif S_ISCHR(value):
            self.data[6] = 5

        elif S_ISFIFO(value):
            self.data[6] = 6

        # keep track of empty directories
        elif S_ISDIR(value):
            self.data[6] = 4

        self.size = stat.st_size
        self.mode = mode
        self.owner = uname
        self.group = gname
        self.modificationTime = stat.st_mtime
        self.creationTime = stat.st_ctime

        # symlink
        if S_ISLNK(value.st_mode):
            self.extended = os.readlink(path)

        # block device
        if S_ISBLK(value.st_mode) or S_ISCHR(value.st_mode):
            id = '%d,%d' % (os.major(value.st_rdev), os.minor(value.st_rdev))
            self.extended = id

# producers
    # def producerAdd(self, name, maxServices=1, actorFQDN="", actorKey=""):
    #     """
    #     name @0 :Text;
    #     actorFQDN @1 :Text;
    #     maxServices @2 :UInt8;
    #     actorKey  @3 :Text;
    #     """
    #     obj = self.producerNewObj()
    #     obj.maxServices = maxServices
    #     obj.actorFQDN = actorFQDN
    #     obj.actorKey = actorKey
    #     obj.name = name
    #     self.changed = changed
    #     return obj

    # @property
    # def dictFiltered(self):
    #     ddict = self.dbobj.to_dict()
    #     if "data" in ddict:
    #         ddict.pop("data")
    #     return ddict

    def _pre_save(self):
        pass
