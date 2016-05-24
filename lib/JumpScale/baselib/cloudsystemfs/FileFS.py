from JumpScale import j


# maybe this could be switched to http://curlftpfs.sourceforge.net/
class FileFS:
    path = None
    end_type = None
    local_file = None
    is_dir = False
    recursive = False

    def __init__(self,end_type,path,is_dir=False,recursive=False,tempdir=j.dirs.tmpDir,Atype='copy'):
        """
        Initialize connection
        """
        self.logger = j.logger.get('j.sal.cloudfs.FileFS')
        self.Atype = Atype
        self.end_type = end_type
        self.path = path
        self.local_file =  j.sal.fs.getBaseName(self.path)
        self.tmp_local_file=j.sal.fs.getTempFileName(tempdir,'FileFS-')
        self.logger.debug("FileFS: path [%s] file [%s]" % (self.path,self.local_file))
        self.is_dir = is_dir
        self.recursive = recursive


    def exists(self):
        """
        Checks file or directory existance
        """

        return j.sal.fs.exists(self.path)


    def upload(self,uploadPath):
        """
        Store file
        """
        if self.Atype == "move":
            if self.is_dir:
                if self.recursive:
                    self.logger.info("FileFS: (directory) Copying [%s] to path [%s] (recursively)" % (uploadPath,self.path))
                    j.sal.fs.moveDir(uploadPath,self.path)
                else:
                # walk tree and move
                    for file in j.sal.fs.walk(uploadPath, recurse=0):
                        self.logger.info("FileFS: (directory) Copying file [%s] to path [%s]" % (file,self.path))
                        j.sal.fs.moveFile(file,self.path)
            else:
                j.sal.fs.moveFile(uploadPath,self.path)
        else:
            if self.Atype == "copy":
                if self.is_dir:
                    if self.recursive:
                        self.logger.info("FileFS: (directory) Copying [%s] to path [%s] (recursively)" % (uploadPath,self.path))
                        if j.sal.fs.isDir(uploadPath):
                            j.sal.fs.copyDirTree(uploadPath, self.path, update=True) # was copyDir !!
                        else:
                            j.sal.fs.copyFile(uploadPath, self.path) # was copyDir !!
                    else:
                    # walk tree and copy
                        for file in j.sal.fs.walk(uploadPath, recurse=0):
                            self.logger.info("FileFS: (directory) Copying file [%s] to path [%s]" % (file,self.path))
                            j.sal.fs.copyFile(file,self.path)
                else:
                    j.sal.fs.copyFile(uploadPath,self.path)


    def download(self):
        """
        Download file
        """
        return self.path

    def cleanup(self):
        """
        If needed umount and cleanup
        """
