from JumpScale import j
from JumpScale.tools.zip.ZipFile import ZipFile
import os


class GitHubFactory(object):
    def __init__(self):
        self.__jslocation__ = "j.clients.github"

    def getClient(self, account, reponame, branch='master', executor=j.tools.executor.getLocal()):
        return GitHubClient(account, reponame, branch, executor)

class GitHubClient(object):
    def __init__(self, account, reponame, branch='master', executor=j.tools.executor.getLocal()):
        self.executor = executor
        self.cuisine = executor.cuisine
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
    def getGitRepoArgs(self, url="", dest=None, login=None, passwd=None, reset=False, branch=None, ssh="auto", codeDir=None):
        """
        Extracts and returns data useful in cloning a Git repository.

        Args:
            url (str): the HTTP/GIT URL of the Git repository to clone from. eg: 'https://github.com/odoo/odoo.git'
            dest (str): the local filesystem path to clone to
            login (str): authentication login name (only for http)
            passwd (str): authentication login password (only for http)
            reset (boolean): if True, any cached clone of the Git repository will be removed
            branch (str): branch to be used
            ssh if auto will check if ssh-agent loaded, if True will be forced to use ssh for git

        #### Process for finding authentication credentials (NOT IMPLEMENTED YET)

        - first check there is an ssh-agent and there is a key attached to it, if yes then no login & passwd will be used & method will always be git
        - if not ssh-agent found
            - then we will check if url is github & ENV argument GITHUBUSER & GITHUBPASSWD is set
                - if env arguments set, we will use those & ignore login/passwd arguments
            - we will check if login/passwd specified in URL, if yes willl use those (so they get priority on login/passwd arguments)
            - we will see if login/passwd specified as arguments, if yes will use those
        - if we don't know login or passwd yet then
            - login/passwd will be fetched from local git repo directory (if it exists and reset==False)
        - if at this point still no login/passwd then we will try to build url with anonymous


        #### Process for defining branch

        - if branch arg: None
            - check if git directory exists if yes take that branch
            - default to 'master'
        - if it exists, use the branch arg

        Returns:
            (repository_host, repository_type, repository_account, repository_name,branch, login, passwd)

            - repository_type http or git

        Remark:
            url can be empty, then the git params will be fetched out of the git configuration at that path
        """

        if url == "":
            if dest == None:
                raise RuntimeError("dest cannot be None (url is also '')")
            if not self.cuisine.core.dir_exists(dest):
                raise RuntimeError(
                    "Could not find git repo path:%s, url was not specified so git destination needs to be specified." % (dest))

        if login == None and url.find("github.com/") != -1:
            # can see if there if login & passwd in OS env
            # if yes fill it in
            if "GITHUBUSER" in self.cuisine.bash.environ.keys():
                login = self.cuisine.bash.environGet("GITHUBUSER")

            if "GITHUBPASSWD" in os.environ.keys():
                passwd = self.cuisine.bash.environGet("GITHUBPASSWD")



        protocol, repository_host, repository_account, repository_name, repository_url = j.do.rewriteGitRepoUrl(
            url=url, login=login, passwd=passwd, ssh=ssh)

        repository_type = repository_host.split(
            '.')[0] if '.' in repository_host else repository_host

        if not dest:
            if codeDir == None:
                codeDir = self.executor.cuisine.core.dir_paths['codeDir']

            dest = '%(codedir)s/%(type)s/%(account)s/%(repo_name)s' % {
                'codedir': codeDir,
                'type': repository_type.lower(),
                'account': repository_account.lower(),
                'repo_name': repository_name,
            }

        if reset:
            self.cuisine.core.dir_remove(dest)

        # self.createDir(dest)

        return repository_host, repository_type, repository_account, repository_name, dest, repository_url

    def pullGitRepo(self, url="", dest=None, login=None, passwd=None, depth=1, ignorelocalchanges=False, reset=False, branch=None, revision=None, ssh="auto", codeDir=None):
        """
        will clone or update repo
        if dest == None then clone underneath: /opt/code/$type/$account/$repo
        will ignore changes !!!!!!!!!!!

        @param ssh ==True means will checkout ssh
        @param ssh =="first" means will checkout sss first if that does not work will go to http
        """

        if ssh == "first":
            try:
                return self.pullGitRepo(url, dest, login, passwd, depth, ignorelocalchanges, reset, branch, revision, True)
            except Exception as e:
                return self.pullGitRepo(url, dest, login, passwd, depth, ignorelocalchanges, reset, branch, revision, False)
            raise RuntimeError(
                "Could not checkout, needs to be with ssh or without.")

        base, provider, account, repo, dest, url = self.getGitRepoArgs(
            url, dest, login, passwd, reset=reset, ssh=ssh, codeDir=codeDir)

        if dest is None and branch is None:
            branch = "master"
        elif branch is None and dest is not None and j.sal.fs.exists(dest):
            # if we don't specify the branch, try to find the currently
            # checkedout branch
            if self.executor.exists(dest):
                cmd = 'cd %s; git rev-parse --abbrev-ref HEAD' % dest
                rc, out = self.executor.execute(cmd, die=False, showout=False)
                if rc == 0:
                    branch = out.strip()
                # if we can't retreive current branch, use master as default
                else:
                    branch = 'master'
            else:
                branch = 'master'

        checkdir = "%s/.git" % (dest)
        if self.executor.exists(checkdir):
            if ignorelocalchanges:
                print(("git pull, ignore changes %s -> %s" % (url, dest)))
                cmd = "cd %s;git fetch" % dest
                if depth != None:
                    cmd += " --depth %s" % depth
                self.executor.execute(cmd)
                if branch != None:
                    print("reset branch to:%s" % branch)
                    self.executor.execute(
                        "cd %s;git reset --hard origin/%s" % (dest, branch), timeout=600)
            else:
                # pull
                print(("git pull %s -> %s" % (url, dest)))
                if url.find("http") != -1:
                    print("http")
                    if branch != None:
                        cmd = "cd %s;git -c http.sslVerify=false pull origin %s" % (
                            dest, branch)
                    else:
                        cmd = "cd %s;git -c http.sslVerify=false pull" % dest
                else:
                    if branch != None:
                        cmd = "cd %s;git pull origin %s" % (dest, branch)
                    else:
                        cmd = "cd %s;git pull" % dest
                self.executor.execute(cmd, timeout=600)
        else:
            print(("git clone %s -> %s" % (url, dest)))
            extra = ""
            if depth and depth != 0:
                extra = "--depth=%s" % depth
            if url.find("http") != -1:
                if branch != None:
                    cmd = "cd %s;git -c http.sslVerify=false clone %s --single-branch -b %s %s %s" % (
                        j.sal.fs.getParent(dest), extra, branch, url, dest)
                else:
                    cmd = "cd %s;git -c http.sslVerify=false clone %s  %s %s" % (
                        j.sal.fs.getParent(dest), extra, url, dest)
            else:
                if branch != None:
                    cmd = "cd %s;git clone %s --single-branch -b %s %s %s" % (
                        j.sal.fs.getParent(dest), extra, branch, url, dest)
                else:
                    cmd = "cd %s;git clone %s  %s %s" % (
                        j.sal.fs.getParent(dest), extra, url, dest)

            print(cmd)

            if depth != None:
                cmd += " --depth %s" % depth
            self.executor.execute(cmd, timeout=600)

        if revision != None:
            cmd = "cd %s;git checkout %s" % (dest, revision)
            print(cmd)
            self.executor.execute(cmd, timeout=600)

        return dest
