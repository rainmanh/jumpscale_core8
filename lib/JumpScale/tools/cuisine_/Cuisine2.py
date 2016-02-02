from __future__ import with_statement
import re
from JumpScale import j
import copy


# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Many ideas & lines of code have been taken from:
#
# Project   : Cuisine - Functions to write Fabric recipes
# -----------------------------------------------------------------------------
# License   : Revised BSD License
# -----------------------------------------------------------------------------
# Authors   : Sebastien Pierre                            <sebastien@ffctn.com>
#             Thierry Stiegler   (gentoo port)     <thierry.stiegler@gmail.com>
#             Jim McCoy (distro checks and rpm port)      <jim.mccoy@gmail.com>
#             Warren Moore (zypper package)               <warren@wamonite.com>
#             Lorenzo Bivens (pkgin package)          <lorenzobivens@gmail.com>
#             kristof de spiegeleer                 kristof@incubaid.com
# -----------------------------------------------------------------------------
# Creation  : 26-Apr-2010
# Last mod  : Nov-2015
# -----------------------------------------------------------------------------
#
# modified by Jumpscale authors & repackaged, also lots of new modules in this directory & different approach


import base64, hashlib, os, re, string, tempfile, subprocess, types, threading, sys
import tempfile, functools
import platform


NOTHING                 = base64
RE_SPACES               = re.compile("[\s\t]+")
STRINGIFY_MAXSTRING     = 80
STRINGIFY_MAXLISTSTRING = 20
MAC_EOL                 = "\n"
UNIX_EOL                = "\n"
WINDOWS_EOL             = "\r\n"

# MODE_LOCAL              = "MODE_LOCAL"
# MODE_SUDO               = "MODE_SUDO"

# SUDO_PASSWORD           = "CUISINE_SUDO_PASSWORD"
# OPTION_PACKAGE          = "CUISINE_OPTION_PACKAGE"
# OPTION_PYTHON_PACKAGE   = "CUISINE_OPTION_PYTHON_PACKAGE"
# OPTION_OS_FLAVOUR       = "CUISINE_OPTION_OS_FLAVOUR"
# OPTION_USER             = "CUISINE_OPTION_USER"
# OPTION_GROUP            = "CUISINE_OPTION_GROUP"
# OPTION_HASH             = "CUISINE_OPTION_HASH"


def stringify( value ):
    """Turns the given value in a user-friendly string that can be displayed"""
    if   type(value) in (str, unicode, bytes) and len(value) > STRINGIFY_MAXSTRING:
        return "{0}...".format(value[0:STRINGIFY_MAXSTRING])
    elif type(value) in (list, tuple) and len(value) > 10:
        return"[{0},...]".format(", ".join([stringify(_) for _ in value[0:STRINGIFY_MAXLISTSTRING]]))
    else:
        return str(value)

def shell_safe( path ):
    SHELL_ESCAPE            = " '\";`|"
    """Makes sure that the given path/string is escaped and safe for shell"""
    path= "".join([("\\" + _) if _ in SHELL_ESCAPE else _ for _ in path])
    return path


def is_ok( text ):
    """Tells if the given text ends with "OK", swallowing trailing blanks."""
    return text.find("**OK**")!=-1

def text_detect_eol(text):
    # FIXME: Should look at the first line
    if text.find("\r\n") != -1:
        return WINDOWS_EOL
    elif text.find("\n") != -1:
        return UNIX_EOL
    elif text.find("\r") != -1:
        return MAC_EOL
    else:
        return "\n"

def text_get_line(text, predicate):
    """Returns the first line that matches the given predicate."""
    for line in text.split("\n"):
        if predicate(line):
            return line
    return ""

def text_normalize(text):
    """Converts tabs and spaces to single space and strips the text."""
    return RE_SPACES.sub(" ", text).strip()

def text_nospace(text):
    """Converts tabs and spaces to single space and strips the text."""
    return RE_SPACES.sub("", text).strip()

def text_replace_line(text, old, new, find=lambda old, new: old == new, process=lambda _: _):
    """Replaces lines equal to 'old' with 'new', returning the new
    text and the count of replacements.

    Returns: (text, number of lines replaced)

    `process` is a function that will pre-process each line (you can think of
    it as a normalization function, by default it will return the string as-is),
    and `find` is the function that will compare the current line to the
    `old` line.

    The finds the line using `find(process(current_line), process(old_line))`,
    and if this matches, will insert the new line instead.
    """
    res = []
    replaced = 0
    eol = text_detect_eol(text)
    for line in text.split(eol):
        if find(process(line), process(old)):
            res.append(new)
            replaced += 1
        else:
            res.append(line)
    return eol.join(res), replaced

def text_replace_regex(text, regex, new, **kwargs):
    """Replace lines that match with the regex returning the new text

    Returns: text

    `kwargs` is for the compatibility with re.sub(),
    then we can use flags=re.IGNORECASE there for example.
    """
    res = []
    eol = text_detect_eol(text)
    for line in text.split(eol):
        res.append(re.sub(regex, new, line, **kwargs))
    return eol.join(res)

def text_ensure_line(text, *lines):
    """Ensures that the given lines are present in the given text,
    otherwise appends the lines that are not already in the text at
    the end of it."""
    eol = text_detect_eol(text)
    res = list(text.split(eol))
    if res[0] == '' and len(res) == 1:
        res = list()
    for line in lines:
        assert line.find(eol) == -1, "No EOL allowed in lines parameter: " + repr(line)
        found = False
        for l in res:
            if l == line:
                found = True
                break
        if not found:
            res.append(line)
    return eol.join(res)

def text_strip_margin(text, margin="|"):
    """Will strip all the characters before the left margin identified
    by the `margin` character in your text. For instance

    ```
            |Hello, world!
    ```

    will result in

    ```
    Hello, world!
    ```
    """
    res = []
    eol = text_detect_eol(text)
    for line in text.split(eol):
        l = line.split(margin, 1)
        if len(l) == 2:
            _, line = l
            res.append(line)
    return eol.join(res)

# def text_template(text, variables):
#     """Substitutes '${PLACEHOLDER}'s within the text with the
#     corresponding values from variables."""
#     template = string.Template(text)
#     return template.safe_substitute(variables)



from CuisineInstaller import CuisineInstaller
from CuisineInstallerDevelop import CuisineInstallerDevelop
from CuisineSystemd import CuisineSystemd
from CuisineUpstart import CuisineUpstart
from CuisinePackage import CuisinePackage
from CuisineProcess import CuisineProcess
from CuisinePIP import CuisinePIP
from CuisineNet import CuisineNet
from CuisineSSH import CuisineSSH
from CuisineNS import CuisineNS
from CuisineUser import CuisineUser
from CuisineGit import CuisineGit
from CuisineBuilder import CuisineBuilder
from CuisineGroup import CuisineGroup
from ActionDecorator import ActionDecorator
from CuisineGolang import CuisineGolang

class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine"

class OurCuisine():

    def __init__(self,executor):
        self.cd="/"

        self.executor=executor

        self._installer = None
        self._platformtype=None
        self._id=None
        self._package=None
        self._upstart=None
        self._systemd=None
        self._installerdevelop=None
        self._process=None
        self._hostname=""
        self._pip=None
        self._ns=None
        self._ssh=None
        self._net=None
        self._group=None
        self._user=None
        self._git=None
        self._builder=None
        self._bash=None
        self._avahi=None
        self._tmux=None
        self._golang=None
        self.cuisine=self
        self._fqn=""
        if self.executor.type=="ssh":
            self.runid="cuisine:%s:%s"%(self.executor.addr,self.executor.port)
        else:
            self.runid="cuisine:local"
        self.done=[]

    @property
    def package(self):
        if self._package==None:

            self._package=CuisinePackage(self.executor,self)
        return self._package

    @property
    def upstart(self):
        if self._upstart==None:
            self._upstart=CuisineUpstart(self.executor,self)
        return self._upstart

    @property
    def systemd(self):
        if self._systemd==None:
            self._systemd=CuisineSystemd(self.executor,self)
        return self._systemd

    @property
    def process(self):
        if self._process==None:
            self._process=CuisineProcess(self.executor,self)
        return self._process

    @property
    def pip(self):
        if self._pip==None:
            self._pip=CuisinePIP(self.executor,self)
        return self._pip


    @property
    def golang(self):
        if self._golang==None:
            self._golang=CuisineGolang(self.executor,self)
        return self._golang

    @property
    def builder(self):
        if self._builder==None:
            self._builder=CuisineBuilder(self.executor,self)
        return self._builder

    @property
    def id(self):
        if self._id==None:
            if "addr" in self.executor.__dict__:
                self._id="%s:%s"%(self.executor.addr,self.executor.port)
            else:
                self._id=""
        return self._id

    @property
    def platformtype(self):
        if self._platformtype==None:
            self._platformtype=j.core.platformtype.get(self.executor)
        return self._platformtype

    @property
    def installer(self):
        if self._installer==None:
            self._installer=CuisineInstaller(self.executor,self)
        return self._installer

    @property
    def installerdevelop(self):
        if self._installerdevelop==None:
            self._installerdevelop=CuisineInstallerDevelop(self.executor,self)
        return self._installerdevelop

    @property
    def ns(self):
        if self._ns==None:
            self._ns=CuisineNS(self.executor,self)
        return self._ns

    @property
    def ssh(self):
        if self._ssh==None:
            self._ssh=CuisineSSH(self.executor,self)
        return self._ssh

    @property
    def avahi(self):
        if self._avahi==None:
            self._avahi=j.tools.avahi.get(self,self.executor)
        return self._avahi

    @property
    def tmux(self):
        if self._tmux==None:
            self._tmux=j.sal.tmux.get(self,self.executor)
        return self._tmux

    @property
    def bash(self):
        if self._bash==None:
            self._bash=j.tools.bash.get(self,self.executor)
        return self._bash

    @property
    def net(self):
        if self._net==None:
            self._net=CuisineNet(self.executor,self)
        return self._net


    @property
    def user(self):
        if self._user==None:
            self._user=CuisineUser(self.executor,self)
        return self._user

    @property
    def group(self):
        if self._group==None:
            self._group=CuisineGroup(self.executor,self)
        return self._group

    @property
    def git(self):
        if self._git==None:
            self._git=CuisineGit(self.executor,self)
        return self._git


    # =============================================================================
    #
    # SYSTEM
    #
    # =============================================================================

    def system_uuid_alias_add(self):
        """Adds system UUID alias to /etc/hosts.
        Some tools/processes rely/want the hostname as an alias in
        /etc/hosts e.g. `127.0.0.1 localhost <hostname>`.
        """
        with mode_sudo():
            old = "127.0.0.1 localhost"
            new = old + " " + system_uuid()
            file_update('/etc/hosts', lambda x: text_replace_line(x, old, new)[0])

    def system_uuid(self):
        """Gets a machines UUID (Universally Unique Identifier)."""
        return self.sudo('dmidecode -s system-uuid | tr "[A-Z]" "[a-z]"')

    # # =============================================================================
    # #
    # # RSYNC
    # #
    # # =============================================================================

    # def rsync(self,local_path, remote_path, compress=True, progress=False, verbose=True, owner=None, group=None):
    #     """Rsyncs local to remote, using the connection's host and user."""
    #     options = "-a"
    #     if compress: options += "z"
    #     if verbose:  options += "v"
    #     if progress: options += " --progress"
    #     if owner or group:
    #         assert owner and group or not owner
    #         options += " --chown={0}{1}".format(owner or "", ":" + group if group else "")
    #     with mode_local():
    #         self.run("rsync {options} {local} {user}@{host}:{remote}".format(
    #             options = options,
    #             host    = host(),
    #             user    = user(),
    #             local   = local_path,
    #             remote  = remote_path,
    #         ))

    # =============================================================================
    #
    # LOCALE
    #
    # =============================================================================

    def locale_check(self,locale):
        locale_data = self.sudo("locale -a | egrep '^%s$' ; true" % (locale,))
        return locale_data == locale

    def locale_ensure(self,locale):
        if not locale_check(locale):
            with fabric.context_managers.settings(warn_only=True):
                self.sudo("/usr/share/locales/install-language-pack %s" % (locale,))
            self.sudo("dpkg-reconfigure locales")

    # =============================================================================
    #
    # FILE OPERATIONS
    #
    # =============================================================================


    # def file_local_read(self,location):
    #     """Reads a *local* file from the given location, expanding '~' and
    #     shell variables."""
    #     p = os.path.expandvars(os.path.expanduser(location))
    #     f = file(p, 'rb')
    #     t = f.read()
    #     f.close()
    #     return t



    def file_backup(self,location, suffix=".orig", once=False):
        """Backups the file at the given location in the same directory, appending
        the given suffix. If `once` is True, then the backup will be skipped if
        there is already a backup file."""
        backup_location = location + suffix
        if once and self.file_exists(backup_location):
            return False
        else:
            return self.run("cp -a {0} {1}".format(
                shell_safe(location),
                shell_safe(backup_location)
            ))

    def file_get_tmp_path(self,basepath=""):
        if basepath=="":
            return "/tmp/%s"%j.data.idgenerator.generateXCharID(10)
        else:
            return "/tmp/%s"%basepath


    def file_download(self,url,to,overwrite=True,retry=3,timeout=0,login="",passwd="",minspeed=0,multithread=False,expand=False):
        """
        download from url
        @return path of downloaded file
        @param to is destination
        @param minspeed is kbytes per sec e.g. 50, if less than 50 kbytes during 10 min it will restart the download (curl only)
        @param when multithread True then will use aria2 download tool to get multiple threads
        """

        if expand:
            destdir=to
            to=self.file_get_tmp_path(j.sal.fs.getBaseName(url))

        if overwrite:
            if self.file_exists(to):
                self.file_unlink(to)
                self.file_unlink("%s.downloadok"%to)
        if not (self.file_exists(to) and self.file_exists("%s.downloadok"%to)):

            self.createDir(j.sal.fs.getDirName(to))

            if multithread==False:
                minspeed=0
                if minspeed!=0:
                    minsp="-y %s -Y 600"%(minspeed*1024)
                else:
                    minsp=""
                if login:
                    user="--user %s:%s "%(login,passwd)
                else:
                    user=""

                cmd = "curl '%s' -o '%s' %s %s --connect-timeout 5 --retry %s --retry-max-time %s"%(url,to,user,minsp,retry,timeout)
                if self.file_exists(to):
                    cmd += " -C -"
                print(cmd)
                self.file_unlink("%s.downloadok"%to)
                rc, out = self.run(cmd, die=False)
                if rc == 33: # resume is not support try again withouth resume
                    self.file_unlink(to)
                    cmd = "curl '%s' -o '%s' %s %s --connect-timeout 5 --retry %s --retry-max-time %s"%(url,to,user,minsp,retry,timeout)
                    rc, out = self.run(cmd, die=False)
                if rc > 0:
                    raise RuntimeError("Could not download:{}.\nErrorcode: {}".format(url, rc))
                else:
                    self.touch("%s.downloadok"%to)
            else:
                raise RuntimeError("not implemented yet")

        if expand:
            self.file_expand(to,destdir)

    def file_expand(self,path,to):
        if path.endswith(".tar.gz") or path.endswith(".tgz"):
            cmd="tar -C %s -xzf %s"%(to,path)
            self.cuisine.run(cmd)
        else:
            raise RuntimeError("not supported yet")


    def touch(self,path):
        self.file_write(path,"")

    def file_read(self,location, default=None):
        """Reads the *remote* file at the given location, if default is not `None`,
        default will be returned if the file does not exist."""

        if default is None:
            assert self.file_exists(location), "cuisine.file_read: file does not exists {0}".format(location)
        elif not self.file_exists(location):
            return default


        frame = self.file_base64(location)

        return base64.b64decode(frame).decode()


    def file_exists(self,location):
        """Tests if there is a *remote* file at the given location."""
        return is_ok(self.run('test -e %s && echo **OK** ; true' % (shell_safe(location)),showout=False))

    def file_is_file(self,location):
        return is_ok(self.run("test -f %s && echo **OK** ; true" % (shell_safe(location)),showout=False))

    def file_is_dir(self,location):
        return is_ok(self.run("test -d %s && echo **OK** ; true" % (shell_safe(location)),showout=False))

    def file_is_link(self,location):
        return is_ok(self.run("test -L %s && echo **OK** ; true" % (shell_safe(location)),showout=False))


    def file_attribs(self,location, mode=None, owner=None, group=None):
        """Updates the mode/owner/group for the remote file at the given
        location."""
        return self.dir_attribs(location, mode, owner, group, False)


    def file_attribs_get(self,location):
        """Return mode, owner, and group for remote path.
        Return mode, owner, and group if remote path exists, 'None'
        otherwise.
        """
        if self.file_exists(location):
            fs_check = self.run('stat %s %s' % (shell_safe(location), '--format="%a %U %G"'),showout=False)
            (mode, owner, group) = fs_check.split(' ')
            return {'mode': mode, 'owner': owner, 'group': group}
        else:
            return None

    @property
    def hostname(self):
        if self._hostname=="":
            if self.isMac:
                hostfile="/private/etc/hostname"
            else:
                hostfile="/etc/hostname"
            self._hostname= self.run("cat %s"%hostfile).strip().split(".",1)[0]
        return self._hostname

    @hostname.setter
    def hostname(self,val):
        val=val.strip().lower()
        if self.isMac:
            hostfile="/private/etc/hostname"
            self.file_write(hostfile,val,sudo=True)
        else:
            hostfile="/etc/hostname"
            self.file_write(hostfile,val)
        self.run("hostname %s"%val)
        self._hostname=val
        self.fqn="%s.%s.%s"%(self.name,self.grid,self.domain) #make sure name is reflected in fqn


    @property
    def name(self):
        self._name,self._grid,self._domain=self.fqn.split(".",2)
        return self._name

    @property
    def grid(self):
        self.name
        return self._grid

    @property
    def domain(self):
        self.name
        return self._domain

    @property
    def fqn(self):
        """
        fully qualified domain name  ($name.$grid.$domain)
        """
        if self._fqn==None or self._fqn=="":
            ns=self.ns.hostfile_get()
            if '127.0.1.1' in ns:
                names=ns['127.0.1.1']
                for name in names:
                    if len(name.split("."))>2:
                        self.fqn=name
                        return self.fqn
            raise RuntimeError("fqn was never set, please use cuisine.setIDs()")
        return self._fqn

    @fqn.setter
    def fqn(self,val):
        self._fqn=val
        self.name #will do the splitting
        self.ns.hostfile_set_multiple([["127.0.1.1",self.fqn],["127.0.1.1",self.name],["127.0.1.1",self.name+"."+self.grid]],remove=["127.0.1.1"])

    def setIDs(self,name,grid,domain="aydo.com"):
        self.fqn="%s.%s.%s"%(name,grid,domain)
        self.hostname=name

    @property
    def hostfile(self):
        if self.isMac:
            hostfile="/private/etc/hosts"
        else:
            hostfile="/etc/hosts"
        return self.file_read(hostfile)

    @hostfile.setter
    def hostfile(self,val):
        if self.isMac:
            hostfile="/private/etc/hosts"
            self.file_write(hostfile,val,sudo=True)
        else:
            hostfile="/etc/hosts"
            self.file_write(hostfile,val)

    @actionrun(action=False,force=False)
    def file_write(self,location, content, mode=None, owner=None, group=None, check=False,sudo=False):
        print ("filewrite: %s"%location)
        content=j.data.text.strip(content)
        content2 = content.encode('utf-8')


        sig = hashlib.md5(content2).hexdigest()

        content_base64=base64.b64encode(content2).decode()

        # if sig != self.file_md5(location):
        cmd='echo "%s" | openssl base64 -A -d > %s' % (content_base64, shell_safe(location))
        if sudo:
            cmd="sudo %s"%cmd
        self.run(cmd,showout=False)

        if check:
            file_sig = self.file_md5(location)
            assert sig == file_sig, "File content does not matches file: %s, got %s, expects %s" % (location, repr(file_sig), repr(sig))

        self.file_attribs(location, mode=mode, owner=owner, group=group)


    @actionrun(action=False,force=False)
    def file_ensure(self,location, mode=None, owner=None, group=None):
        """Updates the mode/owner/group for the remote file at the given
        location."""
        if self.file_exists(location):
            self.file_attribs(location,mode=mode,owner=owner,group=group)
        else:
            self.file_write(location,"",mode=mode,owner=owner,group=group)

    @actionrun(action=False,force=False)
    def file_upload_local(self, local, remote):
        """Uploads the local file to the remote location only if the remote location does not
        exists or the content are different."""
        remote_md5 = self.file_md5(remote)
        local_md5 = j.data.hash.md5(local)
        if remote_md5 == local_md5:
            return

        ftp = self.executor.sshclient.getSFTP()
        content = j.tools.path.get(local).text()
        with ftp.open(remote, mode='w+') as f:
            f.write(content)

    @actionrun(action=False,force=False)
    def file_download_local(self,remote, local):
        """Downloads the remote file to localy only if the local location does not
        exists or the content are different."""
        f = j.tools.path.get(local)
        if f.exists():
            remote_md5 = self.file_md5(remote)
            local_md5 = j.data.hash.md5(local)
            if remote_md5 == local_md5:
                return

        content = self.file_read(remote)
        f.write_text(content)


    @actionrun(action=False,force=False)
    def file_update(self,location, updater=lambda x: x):
        """Updates the content of the given by passing the existing
        content of the remote file at the given location to the 'updater'
        function. Return true if file content was changed.

        For instance, if you'd like to convert an existing file to all
        uppercase, simply do:

        >   file_update("/etc/myfile", lambda _:_.upper())

        Or restart service on config change:

        >   if file_update("/etc/myfile.cfg", lambda _: text_ensure_line(_, line)): self.run("service restart")
        """
        assert self.file_exists(location), "File does not exists: " + location
        old_content = self.file_read(location)
        new_content = updater(old_content)
        if (old_content == new_content):
            return False
        # assert type(new_content) in (str, unicode, fabric.operations._AttributeString), "Updater must be like (string)->string, got: %s() = %s" %  (updater, type(new_content))
        self.file_write(location, new_content)
        return True

    @actionrun(action=False,force=False)
    def file_append(self,location, content, mode=None, owner=None, group=None):
        """Appends the given content to the remote file at the given
        location, optionally updating its mode/owner/group."""
        content2 = content.encode('utf-8')
        content_base64=base64.b64encode(content2).decode()
        self.run('echo "%s" | openssl base64 -A -d >> %s' % (content_base64, shell_safe(location)),showout=False)
        self.file_attribs(location, mode=mode, owner=owner, group=group)

    @actionrun(action=False,force=False)
    def file_unlink(self,path):
        if self.file_exists(path):
            self.run("unlink %s" % (shell_safe(path)))

    @actionrun(action=False,force=False)
    def file_link(self,source, destination, symbolic=True, mode=None, owner=None, group=None):
        """Creates a (symbolic) link between source and destination on the remote host,
        optionally setting its mode/owner/group."""
        if self.file_exists(destination) and (not self.file_is_link(destination)):
            raise Exception("Destination already exists and is not a link: %s" % (destination))
        # FIXME: Should resolve the link first before unlinking
        if self.file_is_link(destination):
            self.file_unlink(destination)
        if symbolic:
            self.run('ln -sf %s %s' % (shell_safe(source), shell_safe(destination)))
        else:
            self.run('ln -f %s %s' % (shell_safe(source), shell_safe(destination)))
        self.file_attribs(destination, mode, owner, group)

    @actionrun(action=False,force=False)
    def file_copy(self, source, dest, recursive=False):
        cmd = "cp -v "
        if recursive:
            cmd += "-r "
        cmd += '%s %s' % (source, dest)
        self.run(cmd)

    # SHA256/MD5 sums with openssl are tricky to get working cross-platform
    # SEE: https://github.com/sebastien/cuisine/pull/184#issuecomment-102336443
    # SEE: http://stackoverflow.com/questions/22982673/is-there-any-function-to-get-the-md5sum-value-of-file-in-linux

    @actionrun(action=False,force=False)
    def file_base64(self,location):
        """Returns the base64-encoded content of the file at the given location."""
        res=self.run("cat {0} | python3 -c 'import sys,base64;sys.stdout.write(base64.b64encode(sys.stdin.read().encode()).decode())'".format(shell_safe((location))),debug=False,checkok=False,showout=False)
        if res.find("command not found")!=-1:
            #print could not find python need to install
            self.package.install("python3.5")
            res=self.run("cat {0} | python3 -c 'import sys,base64;sys.stdout.write(base64.b64encode(sys.stdin.read().encode()).decode())'".format(shell_safe((location))),debug=False,checkok=False,showout=False)
        return res

        # else:
        # return self.run("cat {0} | openssl base64".format(shell_safe((location))))

    @actionrun(action=False,force=False)
    def file_sha256(self,location):
        """Returns the SHA-256 sum (as a hex string) for the remote file at the given location."""
        # NOTE: In some cases, self.sudo can output errors in here -- but the errors will
        # appear before the result, so we simply split and get the last line to
        # be on the safe side.
        if self.file_exists(location):
            return self.run("cat {0} | python -c 'import sys,hashlib;sys.stdout.write(hashlib.sha256(sys.stdin.read()).hexdigest())'".format(shell_safe((location))),debug=False,checkok=False,showout=False)
        else:
            return None
        # else:
        #     return self.run('openssl dgst -sha256 %s' % (shell_safe(location))).split("\n")[-1].split(")= ",1)[-1].strip()

    @actionrun(action=False,force=False)
    def file_md5(self, location):
        """Returns the MD5 sum (as a hex string) for the remote file at the given location."""
        # NOTE: In some cases, self.sudo can output errors in here -- but the errors will
        # appear before the result, so we simply split and get the last line to
        # be on the safe side.
        # if cuisine_env[OPTION_HASH] == "python":
        if self.file_exists(location):
            return self.run("md5sum {0} | cut -f 1 -d ' '".format(shell_safe((location))),debug=False,checkok=False,showout=False)
        else:
            return None
        # else:
        #     return self.run('openssl dgst -md5 %s' % (shell_safe(location))).split("\n")[-1].split(")= ",1)[-1].strip()


    # =============================================================================
    #
    # DIRECTORY OPERATIONS
    #
    # =============================================================================

    @actionrun(action=False,force=False)
    def dir_attribs(self,location, mode=None, owner=None, group=None, recursive=False):
        """Updates the mode/owner/group for the given remote directory."""
        print ("set dir attributes:%s"%location)
        recursive = recursive and "-R " or ""
        if mode:
            self.run('chmod %s %s %s' % (recursive, mode,  shell_safe(location)),showout=False)
        if owner:
            self.run('chown %s %s %s' % (recursive, owner, shell_safe(location)),showout=False)
        if group:
            self.run('chgrp %s %s %s' % (recursive, group, shell_safe(location)),showout=False)

    @actionrun(action=False,force=False)
    def dir_exists(self,location):
        """Tells if there is a remote directory at the given location."""
        print ("dir exists:%s"%location)
        return is_ok(self.run('test -d %s && echo **OK** ; true' % (shell_safe(location)),showout=False))

    @actionrun(action=False,force=False)
    def dir_remove(self,location, recursive=True):
        """ Removes a directory """
        print ("dir remove:%s"%location)
        flag = ''
        if recursive:
            flag = 'r'
        if self.dir_exists(location):
            return self.run('rm -%sf %s && echo **OK** ; true' % (flag, shell_safe(location)),showout=False)

    @actionrun(action=False,force=False)
    def dir_ensure(self,location, recursive=True, mode=None, owner=None, group=None):
        """Ensures that there is a remote directory at the given location,
        optionally updating its mode/owner/group.

        If we are not updating the owner/group then this can be done as a single
        ssh call, so use that method, otherwise set owner/group after creation."""
        if not self.dir_exists(location):
            self.run('mkdir %s %s' % (recursive and "-p" or "", shell_safe(location)))
        if owner or group or mode:
            self.dir_attribs(location, owner=owner, group=group, mode=mode, recursive=recursive)

    createDir=dir_ensure

    @actionrun(action=False,force=False)
    def fs_find(self,path,recursive=True,pattern="",findstatement="",type="",contentsearch="",extendinfo=False):
        """
        @param findstatement can be used if you want to use your own find arguments
        for help on find see http://www.gnu.org/software/findutils/manual/html_mono/find.html

        @param pattern e.g. */config/j*

            *   Matches any zero or more characters.
            ?   Matches any one character.
            [string] Matches exactly one character that is a member of the string string.

        @param type

            b    block (buffered) special
            c    character (unbuffered) special
            d    directory
            p    named pipe (FIFO)
            f    regular file
            l    symbolic link

        @param contentsearch
            looks for this content inside the files

        @param extendinfo   : this will return [[$path,$sizeinkb,$epochmod]]

        """
        cmd="find %s"%path
        if recursive==False:
            cmd+=" -maxdepth 1"
        # if contentsearch=="" and extendinfo==False:
        #     cmd+=" -print"
        if pattern!="":
            cmd+=" -path '%s'"%pattern
        if contentsearch!="":
            type="f"

        if type!="":
            cmd+=" -type %s"%type

        if extendinfo:
            cmd+=" -printf '%p||%k||%T@\n'"

        if contentsearch!="":
            cmd+=" -print0 | xargs -r -0 grep -l '%s'"%contentsearch

        out=self.run(cmd,showout=False)
        print (cmd)

        paths=[item.strip() for item in out.split("\n") if item.strip()!=""]
        paths=[item for item in paths if item.startswith("+ find")==False]

        # print cmd

        paths2=[]
        if extendinfo:
            for item in paths:
                if item.find("||")!=-1:
                    path,size,mod=item.split("||")
                    if path.strip()=="":
                        continueH
                    paths2.append([path,int(size),int(float(mod))])
        else:
            paths2=[item for item in paths if item.strip()!=""]

        return paths2

    # -----------------------------------------------------------------------------
    # CORE
    # -----------------------------------------------------------------------------

    @actionrun()
    def sudo(self, cmd, die=True):
        passwd = self.executor.passwd if hasattr(self.executor, "passwd") else ''
        cmd2 = 'echo %s | sudo -S bash -c "%s"' % (passwd, cmd.replace("$", "\$"))
        return self.run(cmd2, die=die)

    @actionrun()
    def run(self,cmd,die=True,debug=None,checkok=False,showout=True,profile=False):
        """
        @param profile, execute the bash profile first
        """
        import copy

        self.executor.curpath=self.cd
        # print ("CMD:'%s'"%cmd)
        if debug!=None:
            debugremember=copy.copy(debug)
            self.executor.debug=debug

        if profile:
            ppath=self.bash.profilePathExists()
            if ppath!=None:
                cmd=". %s;%s"%(ppath,cmd)
            print ("PROFILECMD:%s"%cmd)

        rc,out=self.executor.execute(cmd,checkok=checkok, die=False, combinestdr=True,showout=showout)

        if rc>0:
            items2check=["sudo","wget","curl","git","openssl"]
            next=True
            while next==True:
                next=False
                if out.find("target not found: python3")!=-1 and not "python" in self.done:
                    from IPython import embed
                    print ("DEBUG NOW python3 not found")
                    embed()
                    self.done.append("python")
                    if self.isArch:
                        self.package.install("python3")
                    else:
                        self.package.install("python3.5")
                    next=True

                if out.find("pip3: command not found")!=-1 and not "pip" in self.done:
                    from IPython import embed
                    print ("DEBUG NOW pip3 not found")
                    embed()

                    self.done.append("pip")
                    self.installer.pip()
                    next=True

                if out.lower().find("fatal error")!=-1 and out.lower().find("python.h")!=-1 \
                            and out.lower().find("no such")!=-1\
                            and not "pythondevel" in self.done:
                    from IPython import embed
                    print ("DEBUG NOW pythondevel not found")
                    embed()

                    self.done.append("pythondevel")
                    self.installer.pythonDevelop()
                    next=True

                for package in items2check:
                    if out.find("not found")!=-1 and  out.find(package)!=-1:
                        from IPython import embed
                        print ("DEBUG NOW cmd not found")
                        embed()

                        if not package in self.done:
                            self.done.append(package)
                            self.installer.base()
                            next=True

                if next:
                    rc,out=self.executor.execute(cmd,checkok=checkok, die=False, combinestdr=True,showout=showout)

        if debug!=None:
            self.executor.debug=debugremember
        if rc>0 and die:
            raise RuntimeError("could not execute %s,OUT:\n%s"%(cmd,out))
        out=out.strip()
        # print("output run: %s" % out)
        if die==False:
            return rc,out
        else:
            return out

    def cd(self,path):
        self.cd=path

    def pwd(self):
        return self.cd

    @actionrun()
    def run_script(self,content,profile=False):
        content=j.data.text.lstrip(content)
        if content[-1]!="\n":
            content+="\n"
        if profile:
            ppath=self.bash.profilePathExists()
            if ppath!=None:
                content=". %s\n%s\n"%(ppath,content)
        content+="\necho **DONE**\n"
        path="/tmp/%s.sh"%j.data.idgenerator.generateRandomInt(0,10000)
        self.file_write(location=path, content=content, mode=0o770, owner="root", group="root")
        out=self.run("bash %s"%path,showout=True)
        self.file_unlink(path)


        lastline=out.split("\n")[-1]
        if lastline.find("**DONE**")==-1:
            raise Exception("Could not execute bash script.\n%s\n"%(content))
            # raise Exception("Could not execute bash script.\n%s\nout:%s\n"%(content,out))
        return "\n".join(out.split("\n")[:-1])



    # =============================================================================
    #
    # SHELL COMMANDS
    #
    # =============================================================================

    def command_check(self,command):
        """Tests if the given command is available on the system."""
        return self.run("which '%s' >& /dev/null && echo **OK** ; true" % command).endswith("OK")

    def command_ensure(self,command, package=None):
        """Ensures that the given command is present, if not installs the
        package with the given name, which is the same as the command by
        default."""
        if package is None:
            package = command
        if not self.command_check(command):
            self.package.install(package)
        assert self.command_check(command), \
            "Command was not installed, check for errors: %s" % (command)


    # =============================================================================
    #
    # TMUX
    #
    # =============================================================================



    def tmux_execute_jumpscript(self,script,sessionname="ssh", screenname="js"):
        """
        execute a jumpscript (script as content) in a remote tmux command, the stdout will be returned
        """
        script=j.data.text.lstrip(script)
        if script.find("from JumpScale import j")==-1:
            script="from JumpScale import j\n\n%s"%script
        path="/tmp/jumpscript_temp_%s.py"%j.data.idgenerator.generateRandomInt(1,10000)
        self.file_write(path,script)
        cmd="jspython %s"%path
        c.tmux.executeInScreen(sessionname,screenname,cmd)
        self.file_unlink(path)
        return out

    def execute_jumpscript(self,script):
        """
        execute a jumpscript (script as content) in a remote tmux command, the stdout will be returned
        """
        script=j.data.text.lstrip(script)
        if script.find("from JumpScale import j")==-1:
            script="from JumpScale import j\n\n%s"%script
        path="/tmp/jumpscript_temp_%s.py"%j.data.idgenerator.generateRandomInt(1,10000)
        self.file_write(path,script)
        out=self.run("jspython %s"%path)
        self.file_unlink(path)
        return out


    #####################SYSTEM IDENTIFICATION

    @property
    def isUbuntu(self):
        return "ubuntu" in self.platformtype.platformtypes

    @property
    def isArch(self):
        return "arch" in self.platformtype.platformtypes

    @property
    def isMac(self):
        return "darwin" in self.platformtype.platformtypes

    def __str__(self):
        return "cuisine:%s:%s" % (getattr(self.executor, 'addr', 'local'), getattr(self.executor, 'port'))

    __repr__=__str__
