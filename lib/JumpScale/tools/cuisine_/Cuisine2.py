from __future__ import with_statement

from JumpScale import j
import copy


# j.sal.ubuntu.check()


# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
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

MODE_LOCAL              = "MODE_LOCAL"
MODE_SUDO               = "MODE_SUDO"

SUDO_PASSWORD           = "CUISINE_SUDO_PASSWORD"
OPTION_PACKAGE          = "CUISINE_OPTION_PACKAGE"
OPTION_PYTHON_PACKAGE   = "CUISINE_OPTION_PYTHON_PACKAGE"
OPTION_OS_FLAVOUR       = "CUISINE_OPTION_OS_FLAVOUR"
OPTION_USER             = "CUISINE_OPTION_USER"
OPTION_GROUP            = "CUISINE_OPTION_GROUP"
OPTION_HASH             = "CUISINE_OPTION_HASH"

CMD_APT_GET             = 'DEBIAN_FRONTEND=noninteractive apt-get -q --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" '
SHELL_ESCAPE            = " '\";`|"
STATS                   = None

AVAILABLE_OPTIONS = dict(
    package        = ["apt", "yum", "zypper", "pacman", "emerge", "pkgin", "pkgng"],
    python_package = ["easy_install","pip"],
    os_flavour     = ["linux","bsd"],
    user           = ["linux","bsd"],
    group          = ["linux","bsd"],
    hash           = ["python", "openssl"]
)

DEFAULT_OPTIONS = dict(
    package        = "apt",
    python_package = "pip",
    os_flavour     = "linux",
    user           = "linux",
    group          = "linux",
    hash           = "python"
)

# logging.info("Welcome to Cuisine v{0}".format(VERSION))

# =============================================================================
#
# STATS
#
# =============================================================================

class Stats(object):
    """A work-in-progress class to store cuisine's statistics, so that you
    can have a summary of what has been done."""

    def __init__( self ):
        self.filesRead         = []
        self.filesWritten      = []
        self.packagesInstalled = []

# =============================================================================
#
# DECORATORS
#
# =============================================================================

def stringify( value ):
    """Turns the given value in a user-friendly string that can be displayed"""
    if   type(value) in (str, unicode, bytes) and len(value) > STRINGIFY_MAXSTRING:
        return "{0}...".format(value[0:STRINGIFY_MAXSTRING])
    elif type(value) in (list, tuple) and len(value) > 10:
        return"[{0},...]".format(", ".join([stringify(_) for _ in value[0:STRINGIFY_MAXLISTSTRING]]))
    else:
        return str(value)

def is_sudo():
    return True

def shell_safe( path ):
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

def text_template(text, variables):
    """Substitutes '${PLACEHOLDER}'s within the text with the
    corresponding values from variables."""
    template = string.Template(text)
    return template.safe_substitute(variables)




class OurCuisineFactory:
    def __init__(self):
        self._local=None

    @property
    def local(self):
        if self._local==None:
            self._local=OurCuisine(j.tools.executor.getLocal())
        return self._local

    def get(self,executor=None):
        """
        example:
        executor=j.tools.executor.getSSHBased(addr='localhost', port=22,login="root",passwd="1234)
        cuisine=j.tools.cuisine.get(executor)
        cuisine.upstart_ensure("apache2")

        or if used without executor then will be the local one

        """

        if executor==None:
            executor=j.tools.executor.getLocal()

        return OurCuisine(executor)



class OurCuisine():

    def __init__(self,executor):
        self.cd="/"
        self.executor=executor

    # =============================================================================
    #
    # UPSTART
    #
    # =============================================================================

    def upstart_ensure(self,name):
        """Ensures that the given upstart service is self.running, starting
        it if necessary."""
        status = self,sudo("service %s status" % name,warn_only=True)
        if status.failed:
            status = self.sudo("service %s start" % name)
        return status

    def upstart_reload(self,name):
        """Reloads the given service, or starts it if it is not self.running."""
        status = self.sudo("service %s reload" % name,warn_only=True)
        if status.failed:
            status = self.sudo("service %s start" % name)
        return status

    def upstart_restart(self,name):
        """Tries a `restart` command to the given service, if not successful
        will stop it and start it. If the service is not started, will start it."""
        status = self.sudo("service %s status" % name,warn_only=True)
        if status.failed:
            return self.sudo("service %s start" % name)
        else:
            status = self.sudo("service %s restart" % name)
            if status.failed:
                self.sudo("service %s stop"  % name)
                return self.sudo("service %s start" % name)
            else:
                return status

    def upstart_stop(self,name):
        """Ensures that the given upstart service is stopped."""
        status = self.sudo("service %s status" % name,warn_only=True)
        if status.succeeded:
            status = self.sudo("service %s stop" % name)
        return status


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
        return is_ok(self.run('test -e %s && echo **OK** ; true' % (shell_safe(location))))

    def file_is_file(self,location):
        return is_ok(self.run("test -f %s && echo **OK** ; true" % (shell_safe(location))))

    def file_is_dir(self,location):
        return is_ok(self.run("test -d %s && echo **OK** ; true" % (shell_safe(location))))

    def file_is_link(self,location):
        return is_ok(self.run("test -L %s && echo **OK** ; true" % (shell_safe(location))))


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
            fs_check = self.run('stat %s %s' % (shell_safe(location), '--format="%a %U %G"'))
            (mode, owner, group) = fs_check.split(' ')
            return {'mode': mode, 'owner': owner, 'group': group}
        else:
            return None

    def file_write(self,location, content, mode=None, owner=None, group=None, check=True):
        content2 = content.encode('utf-8')
        sig = hashlib.md5(content2).hexdigest()

        content_base64=base64.b64encode(content2).decode()

        if sig != self.file_md5(location):
            self.run('echo "%s" | openssl base64 -A -d > %s' % (content_base64, shell_safe(location)))

            if check:
                file_sig = self.file_md5(location)
                assert sig == file_sig, "File content does not matches file: %s, got %s, expects %s" % (location, repr(file_sig), repr(sig))

        self.file_attribs(location, mode=mode, owner=owner, group=group)


    def file_ensure(self,location, mode=None, owner=None, group=None, scp=False):
        """Updates the mode/owner/group for the remote file at the given
        location."""
        if self.file_exists(location):
            self.file_attribs(location,mode=mode,owner=owner,group=group)
        else:
            self.file_write(location,"",mode=mode,owner=owner,group=group,scp=scp)


    def file_upload(self, local, remote):
        """Uploads the local file to the remote location only if the remote location does not
        exists or the content are different."""
        remote_md5 = self.file_md5(remote)
        local_md5 = j.tools.hash.md5(local)
        if remote_md5 == local_md5:
            return

        ftp = self.sshclient.getSFTP()
        content = j.tools.path.get(local).text()
        with ftp.open(remote, mode='w+') as f:
            f.write(content)

    def file_download(self,remote, local):
        """Downloads the remote file to localy only if the local location does not
        exists or the content are different."""
        f = j.tools.path.get(local)
        if f.exists():
            remote_md5 = self.file_md5(remote)
            local_md5 = j.tools.hash.md5(local)
            if remote_md5 == local_md5:
                return

        content = self.file_read(remote)
        f.write_text(content)


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


    def file_append(self,location, content, mode=None, owner=None, group=None):
        """Appends the given content to the remote file at the given
        location, optionally updating its mode/owner/group."""
        # TODO: Make sure this openssl command works everywhere, maybe we should use a text_base64_decode?
        self.run('echo "%s" | openssl base64 -A -d >> %s' % (base64.b64encode(content), shell_safe(location)))
        self.file_attribs(location, mode, owner, group)


    def file_unlink(self,path):
        if self.file_exists(path):
            self.run("unlink %s" % (shell_safe(path)))


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

    # SHA256/MD5 sums with openssl are tricky to get working cross-platform
    # SEE: https://github.com/sebastien/cuisine/pull/184#issuecomment-102336443
    # SEE: http://stackoverflow.com/questions/22982673/is-there-any-function-to-get-the-md5sum-value-of-file-in-linux


    def file_base64(self,location):
        """Returns the base64-encoded content of the file at the given location."""
        return self.run("cat {0} | python3 -c 'import sys,base64;sys.stdout.write(base64.b64encode(sys.stdin.read().encode()).decode())'".format(shell_safe((location))),debug=False,checkok=False)
        # else:
        # return self.run("cat {0} | openssl base64".format(shell_safe((location))))


    def file_sha256(self,location):
        """Returns the SHA-256 sum (as a hex string) for the remote file at the given location."""
        # NOTE: In some cases, self.sudo can output errors in here -- but the errors will
        # appear before the result, so we simply split and get the last line to
        # be on the safe side.
        if self.file_exists(location):
            return self.run("cat {0} | python -c 'import sys,hashlib;sys.stdout.write(hashlib.sha256(sys.stdin.read()).hexdigest())'".format(shell_safe((location))),debug=False,checkok=False)
        else:
            return None
        # else:
        #     return self.run('openssl dgst -sha256 %s' % (shell_safe(location))).split("\n")[-1].split(")= ",1)[-1].strip()


    def file_md5(self,location):
        """Returns the MD5 sum (as a hex string) for the remote file at the given location."""
        # NOTE: In some cases, self.sudo can output errors in here -- but the errors will
        # appear before the result, so we simply split and get the last line to
        # be on the safe side.
        # if cuisine_env[OPTION_HASH] == "python":
        if self.file_exists(location):
            return self.run("cat {0} | python -c 'import sys,hashlib;sys.stdout.write(hashlib.md5(sys.stdin.read().encode(\"utf-8\")).hexdigest())'".format(shell_safe((location))),debug=False,checkok=False)
        else:
            return None
        # else:
        #     return self.run('openssl dgst -md5 %s' % (shell_safe(location))).split("\n")[-1].split(")= ",1)[-1].strip()

    # =============================================================================
    #
    # PROCESS OPERATIONS
    #
    # =============================================================================


    def process_find(self,name, exact=False):
        """Returns the pids of processes with the given name. If exact is `False`
        it will return the list of all processes that start with the given
        `name`."""
        is_string = isinstance(name,str) or isinstance(name,unicode)
        # NOTE: ps -A seems to be the only way to not have the grep appearing
        # as well
        if is_string: processes = self.run("ps -A | grep {0} ; true".format(name))
        else:         processes = self.run("ps -A")
        res = []
        for line in processes.split("\n"):
            if not line.strip(): continue
            line = RE_SPACES.split(line,3)
            # 3010 pts/1    00:00:07 gunicorn
            # PID  TTY      TIME     CMD
            # 0    1        2        3
            # We skip lines that are not like we expect them (sometimes error
            # message creep up the output)
            if len(line) < 4: continue
            pid, tty, time, command = line
            if is_string:
                if pid and ((exact and command == name) or (not exact and command.find(name) >= 0)):
                    res.append(pid)
            elif name(line) and pid:
                res.append(pid)
        return res


    def process_kill(self,name, signal=9, exact=False):
        """Kills the given processes with the given name. If exact is `False`
        it will return the list of all processes that start with the given
        `name`."""
        for pid in self.process_find(name, exact):
            self.run("kill -s {0} {1} ; true".format(signal, pid))

    # =============================================================================
    #
    # DIRECTORY OPERATIONS
    #
    # =============================================================================


    def dir_attribs(self,location, mode=None, owner=None, group=None, recursive=False):
        """Updates the mode/owner/group for the given remote directory."""
        recursive = recursive and "-R " or ""
        if mode:
            self.run('chmod %s %s %s' % (recursive, mode,  shell_safe(location)))
        if owner:
            self.run('chown %s %s %s' % (recursive, owner, shell_safe(location)))
        if group:
            self.run('chgrp %s %s %s' % (recursive, group, shell_safe(location)))

    def dir_exists(self,location):
        """Tells if there is a remote directory at the given location."""
        return is_ok(self.run('test -d %s && echo **OK** ; true' % (shell_safe(location))))


    def dir_remove(self,location, recursive=True):
        """ Removes a directory """
        flag = ''
        if recursive:
            flag = 'r'
        if self.dir_exists(location):
            return self.run('rm -%sf %s && echo **OK** ; true' % (flag, shell_safe(location)))

    def dir_ensure(self,location, recursive=False, mode=None, owner=None, group=None):
        """Ensures that there is a remote directory at the given location,
        optionally updating its mode/owner/group.

        If we are not updating the owner/group then this can be done as a single
        ssh call, so use that method, otherwise set owner/group after creation."""
        if not self.dir_exists(location):
            self.run('mkdir %s %s' % (recursive and "-p" or "", shell_safe(location)))
        if owner or group or mode:
            self.dir_attribs(location, owner=owner, group=group, mode=mode, recursive=recursive)


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
        if contentsearch=="" and extendinfo==False:
            cmd+=" -print"
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

        out=self.connection.run(cmd)

        paths=[item.strip() for item in out.split("\n")]

        # print cmd

        paths2=[]
        if extendinfo:
            for item in paths:
                path,size,mod=item.split("||")
                if path.strip()=="":
                    continue
                paths2.append([path,int(size),int(float(mod))])
        else:
            paths2=[item for item in paths if item.strip()!=""]

        return paths2



    # def changePasswd(self,passwd,login="recovery"):
    #     if len(passwd)<6:
    #         j.events.opserror_critical("Choose longer passwd in changePasswd")
    #     self.connection.run('echo "{username}:{password}" | chpasswd'.format(
    #         username=login,
    #         password=passwd)
    #     )

    def users_get(self):
        users=self.fs_find("/home",recursive=False)
        users=[j.do.getBaseName(item) for item in users if (item.strip()!="" and item.strip("/")!="home")]
        return users

    # -----------------------------------------------------------------------------
    # CORE
    # -----------------------------------------------------------------------------


    def sudo(self,cmd,warn_only=False):
        cmd="sudo -s %s"%cmd
        return self.run(cmd,warn_only)

    def run(self,cmd,warn_only=False,debug=None,checkok=False):
        self.executor.curpath=self.cd
        # print ("CMD:'%s'"%cmd)
        if debug!=None:
            debugremember=copy.copy(debug)
            self.executor.debug=debug

        rc,out=self.executor.execute(cmd,checkok=checkok)

        if debug!=None:
            self.executor.debug=debugremember
        # if rc>0:
        out=out.strip()
        # print("output run: %s" % out)
        return out

    def cd(self,path):
        self.cd=path

    def pwd(self):
        return self.cd

    def run_script(self,content):
        content=j.tools.text.lstrip(content)
        if content[-1]!="\n":
            content+="\n"
        content+="\necho **DONE**\n"
        path="/tmp/%s.sh"%j.tools.idgenerator.generateRandomInt(0,10000)
        self.file_write(location=path, content=content, mode=0o770, owner="root", group="root")
        out=self.run("sh %s"%path)
        self.file_unlink(path)
        lastline=out.split("\n")[-1]
        if lastline.find("**DONE**")==-1:
            raise self.runtimeError("Could not execute bash script.\n%s\nout:%s\n"%(content,out))
        return "\n".join(out.split("\n")[:-1])


    # -----------------------------------------------------------------------------
    # PIP PYTHON PACKAGE MANAGER
    # -----------------------------------------------------------------------------

    def python_package_upgrade(self,package):
        '''
        The "package" argument, defines the name of the package that will be upgraded.
        '''
        self.run('pip install --upgrade %s' % (package))

    def python_package_install(self,package=None,r=None):
        '''
        The "package" argument, defines the name of the package that will be installed.
        The argument "r" referes to the requirements file that will be used by pip and
        is equivalent to the "-r" parameter of pip.
        Either "package" or "r" needs to be provided
        The optional argument "E" is equivalent to the "-E" parameter of pip. E is the
        path to a virtualenv. If provided, it will be added to the pip call.
        '''
        pip="pip"
        if package:
            self.run('pip install %s' %(package))
        elif r:
            self.run('pip install -r %s' %(r))
        else:
            raise Exception("Either a package name or the requirements file has to be provided.")

    def python_package_ensure(self,package=None, r=None):
        '''
        The "package" argument, defines the name of the package that will be ensured.
        The argument "r" referes to the requirements file that will be used by pip and
        is equivalent to the "-r" parameter of pip.
        Either "package" or "r" needs to be provided
        '''
        self.python_package_install(package,r)

    def python_package_remove(self,package):
        '''
        The "package" argument, defines the name of the package that will be ensured.
        The argument "r" referes to the requirements file that will be used by pip and
        is equivalent to the "-r" parameter of pip.
        Either "package" or "r" needs to be provided
        '''
        return self.run('pip uninstall %s' %(package))


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
            self.package_install(package)
        assert self.command_check(command), \
            "Command was not installed, check for errors: %s" % (command)





    # =============================================================================
    #
    # TMUX
    #
    # =============================================================================

    def tmux_execute(self,cmd,interactive=False):
        #@todo (*1*) needs to be improved,should be able to specify names, kill 1 screen when interactive  (windowname)
        res=self.run("tmux has-session -t cmd 2>&1 ;echo")
        if not res.find("session not found")==-1 or res.find("Connection refused")!=-1:
            self.run("tmux new-session -s cmd -d")
        if interactive:
            cmd0="tmux send -t cmd '%s' ENTER"%cmd
            self.run(cmd0)
            out=""
        else:
            self.file_unlink("/tmp/tmuxout")
            cmd0="tmux send -t cmd '%s > /tmp/tmuxout 2>&1;echo **DONE**>> /tmp/tmuxout 2>&1' ENTER"%cmd
            self.run(cmd0)
            out=self.file_read("/tmp/tmuxout")
            self.file_unlink("/tmp/tmuxout")
            if out.find("**DONE**")==-1:
                j.events.opserror_critical("Cannot execute %s on tmux on remote %s.\nError:\n%s"%(cmd,"anode",out))

            out=out.replace("**DONE**","")
        return out


    def tmux_execute_jumpscript(self,script):
        """
        execute a jumpscript (script as content) in a remote tmux command, the stdout will be returned
        """
        script=j.tools.text.lstrip(script)
        path="/tmp/jumpscript_temp_%s.py"%j.tools.idgenerator.generateRandomInt(1,10000)
        self.connection.file_write(path,script)
        out=self.tmux_execute("jspython %s"%path)
        self.connection.file_unlink(path)
        return out



    # =============================================================================
    #
    # ns
    #
    # =============================================================================

    def hostfile_get_ipv4(self,hostfile=""):
        if hostfile=="":
            hostfile = self.file_read('/etc/hosts')
        result={}
        for line in hostfile.split('\n'):
            ipaddr_found = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',line)
            if ipaddr_found!=None:
                ipaddr_found=ipaddr_found.group()
                if ipaddr_found not in result:
                    result[ipaddr_found]=[]
                hosts=line.replace(ipaddr_found,"").strip().split(" ")
                for host in hosts:
                    if host.strip() not in result[ipaddr_found]:
                        result[ipaddr_found].append(host)
        return result


    def hostfile_set(self,name,ipaddr):
        hostfile = self.file_read('/etc/hosts')
        C=""
        result={}
        for line in hostfile.split('\n'):
            ipaddr_found = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',line)
            if ipaddr_found==None:
                C+="%s\n"%line


        res=self.hostfile_get_ipv4(hostfile)
        if not ipaddr in res:
            res[ipaddr]=[name]
        else:
            if name not in res[ipaddr]:
                res[ipaddr].append(name)

        C+="\n"
        for ipaddr,names in res.items():
            namestr=" ".join(names)
            C+="%-20s %s\n"%(ipaddr,namestr)

        self.file_write('/etc/hosts',C)


    def ns_get(self):
        file = self.file_read('/etc/resolv.conf')
        results = []

        for line in file.split('\n'):
            nameserver = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',line)
            if nameserver:
                nameserver = nameserver.string.replace('nameserver', '').strip()
                results.append(nameserver)
        return results

    def ns_set(self, nameservers=[], commit=False):
        if not nameservers:
            raise ValueError('You need to provide at least one DNS server')
        if not isinstance(nameservers, list):
            raise ValueError('nameservers must be a list')

        content = '#EDITED BY JUMPSCALE NETWORK MANAGER\n'
        content += '#DO NOT EDIT THIS FILE BY HAND -- YOUR CHANGES WILL BE OVERWRITTEN\n'

        for ns in nameservers:
            content += 'nameserver %s\n' % ns
        self.file_write('/etc/resolv.conf', content)

    #####################

    def ssh_keygen(self,user, keytype="dsa"):
        """Generates a pair of ssh keys in the user's home .ssh directory."""
        d = self.user_check(user)
        assert d, "User does not exist: %s" % (user)
        home = d["home"]
        key_file = home + "/.ssh/id_%s.pub" % keytype
        if not self.file_exists(key_file):
            self.dir_ensure(home + "/.ssh", mode="0700", owner=user, group=user)
            self.run("ssh-keygen -q -t %s -f '%s/.ssh/id_%s' -N ''" %
                (keytype, home, keytype))
            self.file_attribs(home + "/.ssh/id_%s" % keytype, owner=user, group=user)
            self.file_attribs(home + "/.ssh/id_%s.pub" % keytype, owner=user, group=user)
            return key_file
        else:
            return key_file

    def ssh_authorize(self,user, key):
        """Adds the given key to the '.ssh/authorized_keys' for the given
        user."""
        d = self.user_check(user, need_passwd=False)
        if d==None:
            raise RuntimeError("did not find user:%s"%user)
        group = d["gid"]
        keyf  = d["home"] + "/.ssh/authorized_keys"
        if key[-1] != "\n":
            key += "\n"
        if self.file_exists(keyf):
            d = self.file_read(keyf)
            if self.file_read(keyf).find(key[:-1]) == -1:
                self.file_append(keyf, key)
                return False
            else:
                return True
        else:
            # Make sure that .ssh directory exists, see #42
            self.dir_ensure(os.path.dirname(keyf), owner=user, group=group, mode="700")
            self.file_write(keyf, key,             owner=user, group=group, mode="600")
            return False

    def ssh_unauthorize(self,user, key):
        """Removes the given key to the remote '.ssh/authorized_keys' for the given
        user."""
        key   = key.strip()
        d     = user_check(user, need_passwd=False)
        group = d["gid"]
        keyf  = d["home"] + "/.ssh/authorized_keys"
        if self.file_exists(keyf):
            self.file_write(keyf, "\n".join(_ for _ in file_read(keyf).split("\n") if _.strip() != key), owner=user, group=group, mode="600")
            return True
        else:
            return False

    def user_passwd(self,name, passwd, encrypted_passwd=True):
        """Sets the given user password. Password is expected to be encrypted by default."""
        if passwd.strip()=="":
            raise RuntimeError("passwd cannot be empty")

        c="%s:%s" % (name, passwd)
        encoded_password = base64.b64encode(c.encode('ascii'))
        if encrypted_passwd:
            self.sudo("usermod -p '%s' %s" % (passwd,name))
        else:
            # NOTE: We use base64 here in case the password contains special chars
            # TODO: Make sure this openssl command works everywhere, maybe we should use a text_base64_decode?
            self.sudo("echo %s | openssl base64 -A -d | chpasswd" % (shell_safe(encoded_password)))


    def user_create(self,name, passwd=None, home=None, uid=None, gid=None, shell=None,
        uid_min=None, uid_max=None, encrypted_passwd=True, fullname=None, createhome=True):
        """Creates the user with the given name, optionally giving a
        specific password/home/uid/gid/shell."""
        options = []

        if home:
            options.append("-d '%s'" % (home))
        if uid:
            options.append("-u '%s'" % (uid))
        #if group exists already but is not specified, useradd fails
        if not gid and self.group_check(name):
            gid = name
        if gid:
            options.append("-g '%s'" % (gid))
        if shell:
            options.append("-s '%s'" % (shell))
        if uid_min:
            options.append("-K UID_MIN='%s'" % (uid_min))
        if uid_max:
            options.append("-K UID_MAX='%s'" % (uid_max))
        if fullname:
            options.append("-c '%s'" % (fullname))
        if createhome:
            options.append("-m")
        self.sudo("useradd %s '%s'" % (" ".join(options), name))
        if passwd:
            self.user_passwd(name=name,passwd=passwd,encrypted_passwd=encrypted_passwd)

    def user_check(self,name=None, uid=None, need_passwd=True):
        """Checks if there is a user defined with the given name,
        returning its information as a
        '{"name":<str>,"uid":<str>,"gid":<str>,"home":<str>,"shell":<str>}'
        or 'None' if the user does not exists.
        need_passwd (Boolean) indicates if password to be included in result or not.
            If set to True it parses 'getent shadow' and needs self.sudo access
        """
        assert name!=None or uid!=None,     "user_check: either `uid` or `name` should be given"
        assert name is None or uid is None,"user_check: `uid` and `name` both given, only one should be provided"
        if name != None:
            d = self.run("getent passwd | egrep '^%s:' ; true" % (name))
        elif uid != None:
            d = self.run("getent passwd | egrep '^.*:.*:%s:' ; true" % (uid))
        results = {}
        s = None
        if d:
            d = d.split(":")
            assert len(d) >= 7, "passwd entry returned by getent is expected to have at least 7 fields, got %s in: %s" % (len(d), ":".join(d))
            results = dict(name=d[0], uid=d[2], gid=d[3], fullname=d[4], home=d[5], shell=d[6])
            if need_passwd:
                s = self.sudo("getent shadow | egrep '^%s:' | awk -F':' '{print $2}'" % (results['name']))
                if s: results['passwd'] = s
        if results:
            return results
        else:
            return None

    def user_ensure(self,name, passwd=None, home=None, uid=None, gid=None, shell=None, fullname=None, encrypted_passwd=True,group=None):
        """Ensures that the given users exists, optionally updating their
        passwd/home/uid/gid/shell."""
        d = self.user_check(name)
        if not d:
            self.user_create(name, passwd, home, uid, gid, shell, fullname=fullname, encrypted_passwd=encrypted_passwd)
        else:
            options = []
            if home != None and d.get("home") != home:
                options.append("-d '%s'" % (home))
            if uid != None and d.get("uid") != uid:
                options.append("-u '%s'" % (uid))
            if gid != None and d.get("gid") != gid:
                options.append("-g '%s'" % (gid))
            if shell != None and d.get("shell") != shell:
                options.append("-s '%s'" % (shell))
            if fullname != None and d.get("fullname") != fullname:
                options.append("-c '%s'" % fullname)
            if options:
                self.sudo("usermod %s '%s'" % (" ".join(options), name))
            if passwd:
                self.user_passwd(name=name, passwd=passwd, encrypted_passwd=encrypted_passwd)
        if group!=None:
            self.group_user_add(group=group, user=name)


    def user_remove(self,name, rmhome=None):
        """Removes the user with the given name, optionally
        removing the home directory and mail spool."""
        options = ["-f"]
        if rmhome:
            options.append("-r")
        self.sudo("userdel %s '%s'" % (" ".join(options), name))

    def group_create(self,name, gid=None):
        """Creates a group with the given name, and optionally given gid."""
        options = []
        if gid:
            options.append("-g '%s'" % (gid))
        self.sudo("groupadd %s '%s'" % (" ".join(options), name))

    def group_check(self,name):
        """Checks if there is a group defined with the given name,
        returning its information as:
        '{"name":<str>,"gid":<str>,"members":<list[str]>}'
        or
        '{"name":<str>,"gid":<str>}' if the group has no members
        or
        'None' if the group does not exists."""
        group_data = self.run("getent group | egrep '^%s:' ; true" % (name))
        if len(group_data.split(":")) == 4:
            name, _, gid, members = group_data.split(":", 4)
            return dict(name=name, gid=gid,
                        members=tuple(m.strip() for m in members.split(",")))
        elif len(group_data.split(":")) == 3:
            name, _, gid = group_data.split(":", 3)
            return dict(name=name, gid=gid, members=(''))
        else:
            return None

    def group_ensure(self,name, gid=None):
        """Ensures that the group with the given name (and optional gid)
        exists."""
        d = self.group_check(name)
        if not d:
            self.group_create(name, gid)
        else:
            if gid != None and d.get("gid") != gid:
                self.sudo("groupmod -g %s '%s'" % (gid, name))

    def group_user_check(self,group, user):
        """Checks if the given user is a member of the given group. It
        will return 'False' if the group does not exist."""
        d = self.group_check(group)
        if d is None:
            return False
        else:
            return user in d["members"]

    def group_user_add(self,group, user):
        """Adds the given user/list of users to the given group/groups."""
        assert self.group_check(group), "Group does not exist: %s" % (group)
        if not self.group_user_check(group, user):
            self.sudo("usermod -a -G '%s' '%s'" % (group, user))

    def group_user_ensure(self,group, user):
        """Ensure that a given user is a member of a given group."""
        d = self.group_check(group)
        if not d:
            self.group_ensure("group")
            d = self.group_check(group)
        if user not in d["members"]:
            self.group_user_add(group, user)

    def group_user_del(self,group, user):
            """remove the given user from the given group."""
            assert self.group_check(group), "Group does not exist: %s" % (group)
            if self.group_user_check(group, user):
                    group_for_user = self.run("getent group | egrep -v '^%s:' | grep '%s' | awk -F':' '{print $1}' | grep -v %s; true" % (group, user, user)).splitlines()
                    if group_for_user:
                            self.sudo("usermod -G '%s' '%s'" % (",".join(group_for_user), user))
                    else:
                            self.sudo("usermod -G '' '%s'" % (user))

    def group_remove(self,group=None, wipe=False):
        """ Removes the given group, this implies to take members out the group
        if there are any.  If wipe=True and the group is a primary one,
        deletes its user as well.
        """
        assert self.group_check(group), "Group does not exist: %s" % (group)
        members_of_group = self.run("getent group %s | awk -F':' '{print $4}'" % group)
        members = members_of_group.split(",")
        is_primary_group = self.user_check(name=group)
        if wipe:
            if len(members_of_group):
                for user in members:
                    self.group_user_del(group, user)
            if is_primary_group:
                self.user_remove(group)
            else:
                self.sudo("groupdel %s" % group)
        elif not is_primary_group:
                if len(members_of_group):
                    for user in members:
                        self.group_user_del(group, user)
                self.sudo("groupdel %s" % group)


    #####################PACKAGE MGMT



    def repository_ensure_apt(self,repository):
        self.package_ensure_apt('python-software-properties')
        self.sudo("add-apt-repository --yes " + repository)

    def apt_get(self,cmd):
        cmd    = CMD_APT_GET + cmd
        result = self.sudo(cmd)
        # If the installation process was interrupted, we might get the following message
        # E: dpkg was interrupted, you must manually self.run 'sudo dpkg --configure -a' to correct the problem.
        if "sudo dpkg --configure -a" in result:
            self.sudo("DEBIAN_FRONTEND=noninteractive dpkg --configure -a")
            result = self.sudo(cmd)
        return result

    def package_update_apt(self,package=None):
        if package == None:
            return self.apt_get("-q --yes update")
        else:
            if type(package) in (list, tuple):
                package = " ".join(package)
            return self.apt_get(' upgrade ' + package)

    def package_upgrade_apt(self,distupgrade=False):
        if distupgrade:
            return self.apt_get("dist-upgrade")
        else:
            return self.apt_get("upgrade")

    def package_install_apt(self,package, update=False):
        if update: self.apt_get("update")
        if type(package) in (list, tuple):
            package = " ".join(package)
        return self.apt_get("install " + package)

    def package_ensure_apt(self,package, update=False):
        """Ensure apt packages are installed"""
        if isinstance(package, basestring):
            package = package.split()
        res = {}
        for p in package:
            p = p.strip()
            if not p: continue
            # The most reliable way to detect success is to use the command status
            # and suffix it with OK. This won't break with other locales.
            status = self.run("dpkg-query -W -f='${Status} ' %s && echo **OK**;true" % p)
            if not status.endswith("OK") or "not-installed" in status:
                self.package_install_apt(p)
                res[p]=False
            else:
                if update:
                    self.package_update_apt(p)
                res[p]=True
        if len(res) == 1:
            return res.values()[0]
        else:
            return res

    def package_clean_apt(self,package=None):
        if type(package) in (list, tuple):
            package = " ".join(package)
        return self.apt_get("-y --purge remove %s" % package)

    def package_remove_apt(self,package, autoclean=False):
        self.apt_get('remove ' + package)
        if autoclean:
            self.apt_get("autoclean")
