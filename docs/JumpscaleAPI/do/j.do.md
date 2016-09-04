<!-- toc -->
## j.do

- /opt/jumpscale8/lib/JumpScale/InstallTools.py
- Properties
    - installer
    - BASE
    - debug
    - CODEDIR
    - TMP
    - VARDIR
    - TYPE

### Methods

#### askItemsFromList(*items, msg=''*) 

#### authorizeSSHKey(*remoteipaddr, keyname, login='root', passwd, sshport=22, removeothers*) 

```
this required ssh-agent to be loaded !!!
the keyname is the name of the key as loaded in ssh-agent

if remoteothers==True: then other keys will be removed

```

#### changeDir(*path, create*) 

```
Changes Current Directory
@param path: string (Directory path to be changed to)

```

#### changeLoginPasswdGitRepos(*provider='', account='', name='', login='', passwd='', ssh=True, pushmessage=''*) 

```
walk over all git repo's found in account & change login/passwd

```

#### chdir(*ddir=''*) 

```
if ddir=="" then will go to tmpdir

```

#### checkDirOrLinkToDir(*fullpath*) 

```
check if path is dir or link to a dir

```

#### checkInstalled(*cmdname*) 

```
@param cmdname is cmd to check e.g. curl

```

#### checkSSHAgentAvailable() 

#### chmod(*path, permissions*) 

```
@param permissions e.g. 0o660 (USE OCTAL !!!)

```

#### chown(*path, user*) 

#### copyDependencies(*path, dest*) 

#### copyFile(*source, dest, deletefirst, skipIfExists, makeExecutable*) 

#### copyTree(*source, dest, keepsymlinks, deletefirst, overwriteFiles=True, ignoredir=['.egg-info', '.dist-info'], ignorefiles=['.egg-info'], rsync=True, ssh, sshport=22, recursive=True, rsyncdelete, createdir*) 

```
if ssh format of source or dest is: remoteuser@remotehost:/remote/dir

```

#### createDir(*path*) 

#### delete(*path, force*) 

#### download(*url, to='', overwrite=True, retry=3, timeout, login='', passwd='', minspeed, multithread, curl*) 

```
@return path of downloaded file
@param minspeed is kbytes per sec e.g. 50, if less than 50 kbytes during 10 min it will
    restart the download (curl only)
@param when multithread True then will use aria2 download tool to get multiple threads

```

#### downloadExpandTarGz(*url, destdir, deleteDestFirst=True, deleteSourceAfter=True*) 

#### downloadJumpScaleCore(*dest*) 

#### execute(*command, showout=True, outputStderr=True, useShell=True, log=True, cwd, timeout=1, captureout=True, die=True, async, executor*) 

```
Execute command
@param command: Command to be executed
@param showout: print output line by line while processing the command
@param outputStderr: print error line by line while processing the command
@param useShell: Execute command as a shell command
@param log:
@param cwd: If cwd is not None, the function changes the working directory to cwd before
    executing the child
@param timeout: If not None, raise TimeoutError if command execution time > timeout
@param captureout: If True, returns output of cmd. Else, it returns empty str
@param die: If True, raises error if cmd failed. else, fails silently and returns error in
    the output
@param async: If true, return Process object. DO CLOSE THE PROCESS AFTER FINISHING BY
    process.wait()
@param executor: If not None returns output of executor.execute(....)
@return: (returncode, output, error). output and error defaults to empty string

```

#### executeBashScript(*content='', path, die=True, remote, sshport=22, showout=True, outputStderr=True, sshkey=''*) 

```
@param remote can be ip addr or hostname of remote, if given will execute cmds there

```

#### executeCmds(*cmdstr, showout=True, outputStderr=True, useShell=True, log=True, cwd, timeout=120, captureout=True, die=True*) 

#### executeInteractive(*command*) 

#### exists(*path*) 

#### expandTarGz(*path, destdir, deleteDestFirst=True, deleteSourceAfter*) 

#### findDependencies(*path, deps*) 

#### getBaseName(*path*) 

```
Return the base name of pathname path.

```

#### getBinDirSystem() 

#### getDirName(*path, lastOnly, levelsUp*) 

```
Return a directory name from pathname path.
@param path the path to find a directory within
@param lastOnly means only the last part of the path which is a dir (overrides levelsUp to
    0)
@param levelsUp means, return the parent dir levelsUp levels up
 e.g. ...getDirName("/opt/qbase/bin/something/test.py", levelsUp=0) would return something
 e.g. ...getDirName("/opt/qbase/bin/something/test.py", levelsUp=1) would return bin
 e.g. ...getDirName("/opt/qbase/bin/something/test.py", levelsUp=10) would raise an error

```

#### getFileExtension(*path*) 

#### getGitBranch(*path*) 

#### getGitRepoArgs(*url='', dest, login, passwd, reset, branch, ssh='auto', codeDir, executor*) 

```
Extracts and returns data useful in cloning a Git repository.

Args:
    url (str): the HTTP/GIT URL of the Git repository to clone from. eg:
    'https://github.com/odoo/odoo.git'
    dest (str): the local filesystem path to clone to
    login (str): authentication login name (only for http)
    passwd (str): authentication login password (only for http)
    reset (boolean): if True, any cached clone of the Git repository will be removed
    branch (str): branch to be used
    ssh if auto will check if ssh-agent loaded, if True will be forced to use ssh for git

#### Process for finding authentication credentials (NOT IMPLEMENTED YET)

- first check there is an ssh-agent and there is a key attached to it, if yes then no
    login & passwd will be used & method will always be git
- if not ssh-agent found
    - then we will check if url is github & ENV argument GITHUBUSER & GITHUBPASSWD is set
        - if env arguments set, we will use those & ignore login/passwd arguments
    - we will check if login/passwd specified in URL, if yes willl use those (so they get
    priority on login/passwd arguments)
    - we will see if login/passwd specified as arguments, if yes will use those
- if we don't know login or passwd yet then
    - login/passwd will be fetched from local git repo directory (if it exists and
    reset==False)
- if at this point still no login/passwd then we will try to build url with anonymous

#### Process for defining branch

- if branch arg: None
    - check if git directory exists if yes take that branch
    - default to 'master'
- if it exists, use the branch arg

Returns:
    (repository_host, repository_type, repository_account, repository_name,branch, login,
    passwd)

    - repository_type http or git

Remark:
    url can be empty, then the git params will be fetched out of the git configuration at
    that path

```

#### getGitReposListLocal(*provider='', account='', name='', errorIfNone=True*) 

#### getParent(*path*) 

```
Returns the parent of the path:
/dir1/dir2/file_or_dir -> /dir1/dir2/
/dir1/dir2/            -> /dir1/
TODO: why do we have 2 implementations which are almost the same see getParentDirName()

```

#### getPythonLibSystem(*jumpscale*) 

#### getPythonSiteConfigPath() 

#### getSSHKeyFromAgentPub(*keyname, die=True*) 

#### getSSHKeyPathFromAgent(*keyname, die=True*) 

#### getTimeEpoch() 

```
Get epoch timestamp (number of seconds passed since January 1, 1970)

```

#### getTmpPath(*filename*) 

#### getWalker() 

#### installPackage(*path*) 

#### isDir(*path, followSoftlink*) 

```
Check if the specified Directory path exists
@param path: string
@param followSoftlink: boolean
@rtype: boolean (True if directory exists)

```

#### isExecutable(*path*) 

#### isFile(*path, followSoftlink*) 

```
Check if the specified file exists for the given path
@param path: string
@param followSoftlink: boolean
@rtype: boolean (True if file exists for the given path)

```

#### isLink(*path, checkJunction*) 

```
Check if the specified path is a link
@param path: string
@rtype: boolean (True if the specified path is a link)

```

#### isUnix() 

#### isWindows() 

#### joinPaths(**args*) 

#### list(*path*) 

#### listDirsInDir(*path, recursive, dirNameOnly, findDirectorySymlinks=True*) 

```
Retrieves list of directories found in the specified directory
@param path: string represents directory path to search in
@rtype: list

```

#### listFilesAndDirsInDir(*path, recursive, filter, minmtime, maxmtime, depth, type='fd', followSymlinks=True, listSymlinks*) 

```
Retrieves list of files found in the specified directory
@param path:       directory path to search in
@type  path:       string
@param recursive:  recursively look in all subdirs
@type  recursive:  boolean
@param filter:     unix-style wildcard (e.g. *.py) - this is not a regular expression
@type  filter:     string
@param minmtime:   if not None, only return files whose last modification time > minmtime
    (epoch in seconds)
@type  minmtime:   integer
@param maxmtime:   if not None, only return files whose last modification time < maxmtime
    (epoch in seconds)
@Param depth: is levels deep wich we need to go
@type  maxmtime:   integer
@param type is string with f & d inside (f for when to find files, d for when to find
    dirs)
@rtype: list

```

#### listFilesInDir(*path, recursive, filter, minmtime, maxmtime, depth, case_sensitivity='os', exclude, followSymlinks=True, listSymlinks*) 

```
Retrieves list of files found in the specified directory
@param path:       directory path to search in
@type  path:       string
@param recursive:  recursively look in all subdirs
@type  recursive:  boolean
@param filter:     unix-style wildcard (e.g. *.py) - this is not a regular expression
@type  filter:     string
@param minmtime:   if not None, only return files whose last modification time > minmtime
    (epoch in seconds)
@type  minmtime:   integer
@param maxmtime:   if not None, only return files whose last modification time < maxmtime
    (epoch in seconds)
@Param depth: is levels deep wich we need to go
@type  maxmtime:   integer
@Param exclude: list of std filters if matches then exclude
@rtype: list

```

#### listSSHKeyFromAgent(*keyIncluded*) 

```
returns list of paths

```

#### loadSSHKeys(*path, duration=86400, die*) 

```
will see if ssh-agent has been started
will check keys in home dir
will ask which keys to load
will adjust .profile file to make sure that env param is set to allow ssh-agent to find
    the keys

```

#### loadScript(*path*) 

#### log(*msg, level*) 

#### parseGitConfig(*repopath*) 

```
@param repopath is root path of git repo
@return (giturl,account,reponame,branch,login,passwd)
login will be ssh if ssh is used
login & passwd is only for https

```

#### pullGitRepo(*url='', dest, login, passwd, depth=1, ignorelocalchanges, reset, branch, revision, ssh='auto', executor, codeDir, onlyIfExists*) 

```
will clone or update repo
if dest == None then clone underneath: /opt/code/$type/$account/$repo
will ignore changes !!!!!!!!!!!

@param ssh ==True means will checkout ssh
@param ssh =="first" means will checkout sss first if that does not work will go to http

```

#### pushGitRepos(*message, name='', update=True, provider='', account=''*) 

```
if name specified then will look under code dir if repo with path can be found
if not or more than 1 there will be error
@param provider e.g. git, github

```

#### readFile(*filename*) 

```
Read a file and get contents of that file
@param filename: string (filename to open for reading )
@rtype: string representing the file contents

```

#### readLink(*path*) 

```
Works only for unix
Return a string representing the path to which the symbolic link points.

```

#### removeLinks(*path*) 

```
find all links & remove

```

#### removeSymlink(*path*) 

#### rewriteGitRepoUrl(*url='', login, passwd, ssh='auto'*) 

```
Rewrite the url of a git repo with login and passwd if specified

Args:
    url (str): the HTTP URL of the Git repository. ex: 'https://github.com/odoo/odoo'
    login (str): authentication login name
    passwd (str): authentication login password
    ssh = if True will build ssh url, if "auto" will check if there is ssh-agent available
    & keys are loaded, if yes will use ssh

Returns:
    (repository_host, repository_type, repository_account, repository_name,
    repository_url)

```

#### sendmail(*ffrom, to, subject, msg, smtpuser, smtppasswd, smtpserver='smtp.mandrillapp.com', port=587, html=''*) 

#### symlink(*src, dest, delete*) 

```
dest is where the link will be created pointing to src

```

#### symlinkFilesInDir(*src, dest, delete=True, includeDirs*) 

#### textstrip(*content, ignorecomments*) 

#### touch(*path*) 

#### updateGitRepos(*provider='', account='', name='', message=''*) 

#### whoami() 

#### writeFile(*path, content, strip=True*) 

