from JumpScale import j
from JumpScale.core.system.ZipFile import ZipFile

class GitHubFactory(object):
    def __init__(self):
        pass

    def getClient(self, account, reponame):
        return GitHubClient(account, reponame)


class GitHubClient(object):
    def __init__(self, account, reponame, branch='master'):
        self._account = account
        self._branch = branch
        self._reponame = reponame
        self._url = "http://github.com/%s/%s/archive/%s.zip" % (self._account, self._reponame, branch)
        self._accountdir = j.sal.fs.joinPaths(j.dirs.codeDir, 'github', account)
        self.basedir = j.sal.fs.joinPaths(self._accountdir, "%s-%s" % (reponame, branch))
        self.repokey = "github-%s-%s" % (self._account, self._reponame)

    def export(self):
        if j.sal.fs.exists(self.basedir):
            j.sal.fs.removeDirTree(self.basedir)
        tmpfile = j.sal.fs.getTempFileName()
        j.sal.nettools.download(self._url, tmpfile)
        zp = ZipFile(tmpfile)
        zp.extract(self._accountdir)

    def identify(self):
        return self._branch

    def pullupdate(self):
        # TODO implement this for real
        self.export()


        
