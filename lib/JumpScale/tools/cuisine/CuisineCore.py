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

from __future__ import with_statement
import re
import copy
import base64
import hashlib
import os
import string
import tempfile
import subprocess
import types
import threading
import sys
import functools
import platform

from JumpScale import j
import pygments.lexers
from pygments.formatters import get_formatter_by_name

NOTHING = base64

STRINGIFY_MAXSTRING = 80
STRINGIFY_MAXLISTSTRING = 20


# MODE_LOCAL              = "MODE_LOCAL"
# MODE_SUDO               = "MODE_SUDO"

# SUDO_PASSWORD           = "CUISINE_SUDO_PASSWORD"
# OPTION_PACKAGE          = "CUISINE_OPTION_PACKAGE"
# OPTION_PYTHON_PACKAGE   = "CUISINE_OPTION_PYTHON_PACKAGE"
# OPTION_OS_FLAVOUR       = "CUISINE_OPTION_OS_FLAVOUR"
# OPTION_USER             = "CUISINE_OPTION_USER"
# OPTION_GROUP            = "CUISINE_OPTION_GROUP"
# OPTION_HASH             = "CUISINE_OPTION_HASH"


def stringify(value):
    """Turns the given value in a user-friendly string that can be displayed"""
    if isinstance(value, (str, bytes)) and len(value) > STRINGIFY_MAXSTRING:
        return '{0}...'.format(value[0:STRINGIFY_MAXSTRING])

    if isinstance(value, (list, tuple)) and len(value) > 10:
        return '[{0},...]'.format(', '.join([stringify(_) for _ in value[0:STRINGIFY_MAXLISTSTRING]]))
    return str(value)


def text_detect_eol(text):
    MAC_EOL = "\n"
    UNIX_EOL = "\n"
    WINDOWS_EOL = "\r\n"

    # TODO: Should look at the first line
    if text.find("\r\n") != -1:
        return WINDOWS_EOL
    if text.find("\n") != -1:
        return UNIX_EOL
    if text.find("\r") != -1:
        return MAC_EOL
    return "\n"


def text_get_line(text, predicate):
    """Returns the first line that matches the given predicate."""
    for line in text.split("\n"):
        if predicate(line):
            return line
    return ""


def text_normalize(text):
    """Converts tabs and spaces to single space and strips the text."""
    RE_SPACES = re.compile("[\s\t]+")
    return RE_SPACES.sub(" ", text).strip()


def text_nospace(text):
    """Converts tabs and spaces to single space and strips the text."""
    RE_SPACES = re.compile("[\s\t]+")
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


base = j.tools.cuisine._getBaseClass()


class CuisineCore(base):

    def __init__(self, executor, cuisine):
        base.__init__(self, executor, cuisine)
        self.logger = j.logger.get("j.tools.cuisine.core")
        # print ("***NEW CORE***")
        self.cd = "/"
        self.sudomode = False

    def shell_safe(self, path):
        SHELL_ESCAPE = " '\";`|"
        """Makes sure that the given path/string is escaped and safe for shell"""
        path = "".join([("\\" + _) if _ in SHELL_ESCAPE else _ for _ in path])
        return path

    def getenv(self, refresh=False):
        res = {}
        _, out, _ = self._cuisine.core.run("printenv", profile=False, showout=False, replaceArgs=False)
        for line in out.splitlines():
            if '=' in line:
                name, val = line.split("=", 1)
                name = name.strip()
                val = val.strip().strip("'").strip("\"")
                res[name] = val
        return res

    @property
    def isJS8Sandbox(self):
        def get():
            # TODO: need to implement when sandbox, what is the right check?
            return self.file_exists("/JS8/opt/jumpscale8/bin/libasn1.so.8")
        return self._cache.get("isJS8Sandbox", get)

    @property
    def dir_paths(self):
        res = {}
        env = self.getenv()
        if 'JSBASE' in env:
            res["base"] = env["JSBASE"]
        else:
            if self.dir_exists("/JS8"):
                res["base"] = "/JS8/opt/jumpscale8/"
            elif self.isMac or self.isCygwin:
                res["base"] = "%s/opt/jumpscale8/" % env["HOME"]
            else:
                res["base"] = "/opt/jumpscale8"

        if self.dir_exists('/JS8'):
            res["codeDir"] = "/JS8/code/"
            res["optDir"] = "/JS8/opt/"
            res["varDir"] = "/JS8/optvar/"
        elif self.isMac or self.isCygwin:
            res["codeDir"] = "%s/opt/code/" % env["HOME"]
            res["optDir"] = "%s/opt/" % env["HOME"]
            res["varDir"] = "%s/optvar/" % env["HOME"]
        else:
            res["codeDir"] = "/opt/code"
            res["optDir"] = "/opt"
            res["varDir"] = "/optvar"

        res["appDir"] = "%s/apps" % res["base"]
        res['tmplsDir'] = "%s/templates" % res["base"]
        res["binDir"] = "%s/bin" % res["base"]
        res["cfgDir"] = "%s/cfg" % res["varDir"]
        res["jsLibDir"] = "%s/lib/JumpScale/" % res["base"]
        res["libDir"] = "%s/lib/" % res["base"]
        res["homeDir"] = env["HOME"]
        res["logDir"] = "%s/log" % res["varDir"]
        res["pidDir"] = "%s/pid" % res["varDir"]
        res["tmpDir"] = "%s/tmp" % res["varDir"]
        res["hrdDir"] = "%s/hrd" % res["varDir"]

        res["goDir"] = "%s/go/" % res["varDir"]

        return res

    # =============================================================================
    #
    # SYSTEM
    #
    # =============================================================================

    def pprint(self, text, lexer="bash"):
        """
        @format py3, bash
        """
        text = self.args_replace(text)

        formatter = pygments.formatters.Terminal256Formatter(style=pygments.styles.get_style_by_name("vim"))

        lexer = pygments.lexers.get_lexer_by_name(lexer)  # , stripall=True)
        colored = pygments.highlight(text, lexer, formatter)
        sys.stdout.write(colored)

    def args_replace(self, text):
        """
        replace following args (when jumpscale installed it will take the args from there)
        dirs:
        - $base
        - $appDir
        - $tmplsDir
        - $varDir/
        - $binDir
        - $codeDir
        - $cfgDir
        - $homeDir
        - $jsLibDir
        - $libDir
        - $logDir
        - $pidDir
        - $tmpDir/
        system
        - $hostname

        """
        if "$" in text:
            for key, var in self.dir_paths.items():
                text = text.replace("$%s" % key, var)
                text = text.replace("$%s" % key.lower(), var)
            text = text.replace("$hostname", self.hostname)
        return text

    def system_uuid_alias_add(self):
        """Adds system UUID alias to /etc/hosts.
        Some tools/processes rely/want the hostname as an alias in
        /etc/hosts e.g. `127.0.0.1 localhost <hostname>`.
        """
        with mode_sudo():
            old = "127.0.0.1 localhost"
            new = old + " " + self.system_uuid()
            self.file_update('/etc/hosts', lambda x: text_replace_line(x, old, new)[0])

    def system_uuid(self):
        """Gets a machines UUID (Universally Unique Identifier)."""
        return self.sudo('dmidecode -s system-uuid | tr "[A-Z]" "[a-z]"')

    # =============================================================================
    #
    # LOCALE
    #
    # =============================================================================

    def locale_check(self, locale):
        locale_data = self.sudo("locale -a | egrep '^%s$' ; true" % (locale,))
        return locale_data == locale

    def locale_ensure(self, locale):
        if not self.locale_check(locale):
            with fabric.context_managers.settings(warn_only=True):
                self.sudo("/usr/share/locales/install-language-pack %s" % (locale,))
            self.sudo("dpkg-reconfigure locales")

    # =============================================================================
    #
    # FILE OPERATIONS
    #
    # =============================================================================

    def file_backup(self, location, suffix=".orig", once=False):
        """Backups the file at the given location in the same directory, appending
        the given suffix. If `once` is True, then the backup will be skipped if
        there is already a backup file."""
        backup_location = location + suffix
        if once and self.file_exists(backup_location):
            return False
        else:
            return self.run("cp -a {0} {1}".format(
                location,
                self.shell_safe(backup_location)
            ))[1]

    def file_get_tmp_path(self, basepath=""):
        if basepath == "":
            x = "$tmpDir/%s" % j.data.idgenerator.generateXCharID(10)
        else:
            x = "$tmpDir/%s" % basepath
        x = self.args_replace(x)
        return x

    def file_download(self, url, to, overwrite=True, retry=3, timeout=0, login="",
                      passwd="", minspeed=0, multithread=False, expand=False):
        """
        download from url
        @return path of downloaded file
        @param to is destination
        @param minspeed is kbytes per sec e.g. 50, if less than 50 kbytes during 10 min it will restart the download (curl only)
        @param when multithread True then will use aria2 download tool to get multiple threads
        """

        if expand:
            destdir = to
            to = self.file_get_tmp_path(j.sal.fs.getBaseName(url))

        if overwrite:
            if self.file_exists(to):
                self.file_unlink(to)
                self.file_unlink("%s.downloadok" % to)
        if not (self.file_exists(to) and self.file_exists("%s.downloadok" % to)):

            self.createDir(j.sal.fs.getDirName(to))

            if multithread is False:
                minspeed = 0
                if minspeed != 0:
                    minsp = "-y %s -Y 600" % (minspeed * 1024)
                else:
                    minsp = ""
                if login:
                    user = "--user %s:%s " % (login, passwd)
                else:
                    user = ""

                cmd = "curl -L '%s' -o '%s' %s %s --connect-timeout 10 --retry %s --retry-max-time %s" % (
                    url, to, user, minsp, retry, timeout)
                if self.file_exists(to):
                    cmd += " -C -"
                self.logger.info(cmd)
                self.file_unlink("%s.downloadok" % to)
                rc, out, err = self.run(cmd, die=False)
                if rc == 33:  # resume is not support try again withouth resume
                    self.file_unlink(to)
                    cmd = "curl -L '%s' -o '%s' %s %s --connect-timeout 10 --retry %s --retry-max-time %s" % (
                        url, to, user, minsp, retry, timeout)
                    rc, out, err = self.run(cmd, die=False)
                if rc > 0:
                    raise j.exceptions.RuntimeError("Could not download:{}.\nErrorcode: {}.\n".format(url, rc))
                else:
                    self.touch("%s.downloadok" % to)
            else:
                raise j.exceptions.RuntimeError("not implemented yet")

        if expand:
            self.file_expand(to, destdir)

    def file_expand(self, path, to):
        path = self.args_replace(path)
        to = self.args_replace(to)
        if path.endswith(".tar.gz") or path.endswith(".tgz"):
            cmd = "tar -C %s -xzf %s" % (to, path)
            self.run(cmd)
        else:
            raise j.exceptions.RuntimeError("not supported yet")

    def touch(self, path):
        path = self.args_replace(path)
        self.file_write(path, "")

    def file_read(self, location, default=None):
        import base64
        """Reads the *remote* file at the given location, if default is not `None`,
        default will be returned if the file does not exist."""
        location = self.args_replace(location)
        if default is None:
            assert self.file_exists(location), "cuisine.file_read: file does not exists {0}".format(location)
        elif not self.file_exists(location):
            return default
        frame = self.file_base64(location)
        return base64.decodebytes(frame.encode(errors='replace')).decode()

    def _check_is_ok(self, cmd, location):
        location = self.args_replace(location)
        cmd += ' %s' % location
        rc, out, err = self.run(cmd, showout=False, die=False)
        return rc == 0

    def file_exists(self, location):
        """Tests if there is a *remote* file at the given location."""
        return self._check_is_ok('test -e', location)

    def file_is_file(self, location):
        return self._check_is_ok('test -f', location)

    def file_is_dir(self, location):
        return self._check_is_ok('test -d', location)

    def file_is_link(self, location):
        return self._check_is_ok('test -L', location)

    def file_attribs(self, location, mode=None, owner=None, group=None):
        """Updates the mode/owner/group for the remote file at the given
        location."""
        location = self.args_replace(location)
        return self.dir_attribs(location, mode, owner, group, False)

    def file_attribs_get(self, location):
        """Return mode, owner, and group for remote path.
        Return mode, owner, and group if remote path exists, 'None'
        otherwise.
        """
        location = self.args_replace(location)
        if self.file_exists(location):
            fs_check = self.run('stat %s %s' % (location, '--format="%a %U %G"'), showout=False)[1]
            (mode, owner, group) = fs_check.split(' ')
            return {'mode': mode, 'owner': owner, 'group': group}
        else:
            return None

    @property
    def hostname(self):
        def get():
            if self.isMac or self.isCygwin:
                hostname = self.run("hostname")[1]
            else:
                hostfile = "/etc/hostname"
                rc, out, err = self.run("cat %s" % hostfile, showout=False, replaceArgs=False)
                hostname = out.strip().split(".", 1)[0]
            return hostname
        return self._cache.get("hostname", get)

    @hostname.setter
    def hostname(self, val):
        sudo = self.sudomode = True
        self.sudomode = True

        val = val.strip().lower()
        if self.isMac:
            hostfile = "/private/etc/hostname"
            self.file_write(hostfile, val, sudo=True)
        else:
            hostfile = "/etc/hostname"
            self.file_write(hostfile, val)
        self.run("hostname %s" % val)
        self._hostname = val
        self.ns.hostfile_set(val, '127.0.0.1')

        self.sudomode = sudo

    @property
    def name(self):
        _name, _grid, _domain = self.fqn.split(".", 2)
        return _name

    @property
    def grid(self):
        _name, _grid, _domain = self.fqn.split(".", 2)
        return _grid

    @property
    def domain(self):
        _name, _grid, _domain = self.fqn.split(".", 2)
        return _domain

    @property
    def ns(self):
        return self._cuisine.ns

    @property
    def fqn(self):
        """
        fully qualified domain name  ($name.$grid.$domain)
        """
        def get():
            ns = self.ns.hostfile_get()
            if '127.0.1.1' in ns:
                names = ns['127.0.1.1']
                for name in names:
                    if len(name.split(".")) > 2:
                        fqn = name
                        return fqn
            raise j.exceptions.RuntimeError("fqn was never set, please use cuisine.setIDs()")
        return self._cache.get("fqn", get)

    @fqn.setter
    def fqn(self, val):
        self._cache.set("fqn", val)
        self.name  # will do the splitting
        self.ns.hostfile_set_multiple([["127.0.1.1", self.fqn], ["127.0.1.1", self.name], [
                                      "127.0.1.1", self.name + "." + self.grid]], remove=["127.0.1.1"])

    def setIDs(self, name, grid, domain="aydo.com"):
        self.fqn = "%s.%s.%s" % (name, grid, domain)
        self.hostname = name

    @property
    def hostfile(self):
        def get():
            if self.isMac:
                hostfile = "/private/etc/hosts"
            else:
                hostfile = "/etc/hosts"
            return self.file_read(hostfile)
        return self._cache.get("hostfile", get)

    @hostfile.setter
    def hostfile(self, val):
        if self.isMac:
            hostfile = "/private/etc/hosts"
            self.file_write(hostfile, val, sudo=True)
        else:
            hostfile = "/etc/hosts"
            self.file_write(hostfile, val)

    def upload(self, source, dest=""):
        """
        @param source is on local (where we run the cuisine)
        @param dest is on remote host (on the ssh node)

        will replace $varDir, $codeDir, ... in source using j.dirs.replaceTxtDirVars (is for local cuisine)
        will also replace in dest but then using cuisine.core.args_replace(dest) (so for cuisine host)

        @param dest, if empty then will be same as source very usefull when using e.g. $codeDir

        upload happens using rsync

        """
        if dest == "":
            dest = source
        source = j.dirs.replaceTxtDirVars(source)
        dest = self._cuisine.core.args_replace(dest)
        print("upload local:%s to remote:%s" % (source, dest))
        if self._cuisine.id == 'localhost':
            j.do.copyTree(source, dest, keepsymlinks=True)
            return
        self._executor.sshclient.rsync_up(source, dest)

    def download(self, source, dest=""):
        """
        @param source is on remote host (on the ssh node)
        @param dest is on local (where we run the cuisine)
        will replace $varDir, $codeDir, ...
        - in source but then using cuisine.core.args_replace(dest) (so for cuisine host)
        - in dest using j.dirs.replaceTxtDirVars (is for local cuisine)

        @param dest, if empty then will be same as source very usefull when using e.g. $codeDir

        """
        if dest == "":
            dest = source
        dest = j.dirs.replaceTxtDirVars(dest)
        source = self._cuisine.core.args_replace(source)
        print("download remote:%s to local:%s" % (source, dest))
        if self._cuisine.id == 'localhost':
            j.do.copyTree(source, dest, keepsymlinks=True)
            return
        self._executor.sshclient.rsync_down(source, dest)

    def file_write(self, location, content, mode=None, owner=None, group=None, check=False,
                   sudo=False, replaceArgs=False, strip=True, showout=True, append=False):
        """
        @param append if append then will add to file
        """
        if append:
            content = j.data.text.strip(content)
            C = self.file_read(location)
            C += '\n' + content
            self.file_write(location, C, mode, owner, group, check, sudo, replaceArgs, strip, showout)

        else:
            if showout:
                self.logger.info("write content in %s" % location)
            if strip:
                content = j.data.text.strip(content)

            location = self.args_replace(location)
            if replaceArgs:
                content = self.args_replace(content)

            # if showout:
            #     print ("filewrite: %s"%location)

            self.dir_ensure(j.sal.fs.getParent(location))

            content2 = content.encode('utf-8')

            sig = hashlib.md5(content2).hexdigest()
            # if sig != self.file_md5(location):
            # cmd = 'set -ex && echo "%s" | openssl base64 -A -d > %s' % (content_base64, location)

            if len(content2) > 100000:
                # when contents are too big, bash will crash
                temp = j.sal.fs.getTempFileName()
                j.sal.fs.writeFile(filename=temp, contents=content2, append=False)
                self.upload(temp, location)
            else:
                content_base64 = base64.b64encode(content2).decode()
                # if sig != self.file_md5(location):
                cmd = 'echo "%s" | openssl base64 -A -d > %s' % (content_base64, location)
                res = self.run(cmd, showout=False)
            if check:
                file_sig = self.file_md5(location)
                assert sig == file_sig, "File content does not matches file: %s, got %s, expects %s" % (
                    location, repr(file_sig), repr(sig))

            self.file_attribs(location, mode=mode, owner=owner, group=group)

    def file_ensure(self, location, mode=None, owner=None, group=None):
        """Updates the mode/owner/group for the remote file at the given
        location."""
        location = self.args_replace(location)
        if self.file_exists(location):
            self.file_attribs(location, mode=mode, owner=owner, group=group)
        else:
            self.file_write(location, "", mode=mode, owner=owner, group=group)

    def _file_stream(self, input, output):
        while True:
            piece = input.read(131072)
            if not piece:
                break

            output.write(piece)

        output.close()
        input.close()

    def file_upload_binary(self, local, remote):
        raise NotImplemented("please use upload")

    def file_upload_local(self, local, remote):
        raise NotImplemented("please use download")

    def upload_from_local(self, local, remote):
        raise NotImplemented("please use upload")

    def file_download_binary(self, local, remote):
        raise NotImplemented("please use download")

    def file_download_local(self, remote, local):
        raise NotImplemented("please use download")

    def file_remove_prefix(self, location, prefix, strip=True):
        # look for each line which starts with prefix & remove
        content = self.file_read(location)
        out = ""
        for l in content.split("\n"):
            if strip:
                l2 = l.strip()
            else:
                l2 = l
            if l2.startswith(prefix):
                continue
            out += "%s\n" % l
        self.file_write(location, out)

    def file_update(self, location, updater=lambda x: x):
        """Updates the content of the given by passing the existing
        content of the remote file at the given location to the 'updater'
        function. Return true if file content was changed.

        For instance, if you'd like to convert an existing file to all
        uppercase, simply do:

        >   file_update("/etc/myfile", lambda _: _.upper())

        Or restart service on config change:

        > if file_update("/etc/myfile.cfg", lambda _: text_ensure_line(_, line)): self.run("service restart")
        """
        location = self.args_replace(location)
        assert self.file_exists(location), "File does not exists: " + location
        old_content = self.file_read(location)
        new_content = updater(old_content)
        if old_content == new_content:
            return False
        # assert type(new_content) in (str, unicode,
        # fabric.operations._AttributeString), "Updater must be like
        # (string)->string, got: %s() = %s" %  (updater, type(new_content))
        self.file_write(location, new_content)

        return True

    def file_append(self, location, content, mode=None, owner=None, group=None):
        """Appends the given content to the remote file at the given
        location, optionally updating its mode / owner / group."""
        location = self.args_replace(location)
        content2 = content.encode('utf-8')
        content_base64 = base64.b64encode(content2).decode()
        self.run('echo "%s" | openssl base64 -A -d >> %s' % (content_base64, location), showout=False)
        self.file_attribs(location, mode=mode, owner=owner, group=group)

    def file_unlink(self, path):
        path = self.args_replace(path)
        if self.file_exists(path):
            self.run("unlink %s" % (self.shell_safe(path)), showout=False)

    def file_link(self, source, destination, symbolic=True, mode=None, owner=None, group=None):
        """Creates a (symbolic) link between source and destination on the remote host,
        optionally setting its mode / owner / group."""
        source = self.args_replace(source)
        destination = self.args_replace(destination)
        if self.file_exists(destination) and (not self.file_is_link(destination)):
            raise Exception("Destination already exists and is not a link: %s" % (destination))
        # FIXME: Should resolve the link first before unlinking
        if self.file_is_link(destination):
            self.file_unlink(destination)
        if symbolic:
            self.run('ln -sf %s %s' % (self.shell_safe(source), self.shell_safe(destination)))

        else:
            self.run('ln -f %s %s' % (self.shell_safe(source), self.shell_safe(destination)))

        self.file_attribs(destination, mode, owner, group)

    def file_copy(self, source, dest, recursive=False, overwrite=True):
        source = self.args_replace(source)
        dest = self.args_replace(dest)
        cmd = "cp -v "
        if recursive:
            cmd += "-r "
        if not overwrite:
            if self.isMac:
                cmd += " -n "
            else:
                cmd += " --no-clobber "

        if self.isMac:
            cmd += '%s %s' % (source.rstrip("/"), dest)
            cmd += " 2>&1 >/dev/null ;True"
        else:
            cmd += '%s %s' % (source, dest)

        self.run(cmd)

    def file_move(self, source, dest, recursive=False):
        self.file_copy(source, dest, recursive)
        self.file_unlink(source)

    # SHA256/MD5 sums with openssl are tricky to get working cross-platform
    # SEE: https://github.com/sebastien/cuisine/pull/184#issuecomment-102336443
    # SEE: http://stackoverflow.com/questions/22982673/is-there-any-function-to-get-the-md5sum-value-of-file-in-linux

    def file_base64(self, location):
        """Returns the base64 - encoded content of the file at the given location."""
        location = self.args_replace(location)
        cmd = "cat {0} | base64".format(self.shell_safe((location)))
        rc, out, err = self.run(cmd, debug=False, checkok=False, showout=False)
        return out

    def file_sha256(self, location):
        """Returns the SHA - 256 sum (as a hex string) for the remote file at the given location."""
        # NOTE: In some cases, self.sudo can output errors in here -- but the errors will
        # appear before the result, so we simply split and get the last line to
        # be on the safe side.
        location = self.args_replace(location)
        if self.file_exists(location):
            return self.run("cat {0} | python -c 'import sys,hashlib;sys.stdout.write(hashlib.sha256(sys.stdin.read()).hexdigest())'".format(
                self.shell_safe((location))), debug=False, checkok=False, showout=False)[1]
        else:
            return None
        # else:
        #     return self.run('openssl dgst -sha256 %s' % (location)).split("\n")[-1].split(")= ",1)[-1].strip()

    #

    def file_md5(self, location):
        """Returns the MD5 sum (as a hex string) for the remote file at the given location."""
        # NOTE: In some cases, self.sudo can output errors in here -- but the errors will
        # appear before the result, so we simply split and get the last line to
        # be on the safe side.
        # if cuisine_env[OPTION_HASH] == "python":
        location = self.args_replace(location)
        if self.file_exists(location):
            cmd = "md5sum {0} | cut -f 1 -d ' '".format(self.shell_safe((location)))
            rc, out, err = self.run(cmd, debug=False, checkok=False, showout=False)
            return out
        # return self.run('openssl dgst -md5 %s' % (location)).split("\n")[-1].split(")= ",1)[-1].strip()

    # =============================================================================
    #
    # DIRECTORY OPERATIONS
    #
    # =============================================================================

    def joinpaths(self, *args):
        path = ""
        seperator = "\\"
        if self.isMac or self.isUbuntu or self.isArch:
            seperator = "/"
        for arg in args:
            path += "%s%s" % (seperator, arg)
        return path

    def dir_attribs(self, location, mode=None, owner=None, group=None, recursive=False, showout=False):
        """Updates the mode / owner / group for the given remote directory."""
        location = self.args_replace(location)
        if showout:
            # print ("set dir attributes:%s"%location)
            self.logger.debug('set dir attributes:%s"%location')
        recursive = recursive and "-R " or ""
        if mode:
            self.run('chmod %s %s %s' % (recursive, mode, location), showout=False)
        if owner:
            self.run('chown %s %s %s' % (recursive, owner, location), showout=False)
        if group:
            self.run('chgrp %s %s %s' % (recursive, group, location), showout=False)

    def dir_exists(self, location):
        """Tells if there is a remote directory at the given location."""
        # print ("dir exists:%s"%location)
        return self._check_is_ok('test -d', location)

    def dir_remove(self, location, recursive=True):
        """ Removes a directory """
        location = self.args_replace(location)
        # print("dir remove:%s"%location)
        self.logger.debug("dir remove:%s" % location)
        flag = ''
        if recursive:
            flag = 'r'
        if self.dir_exists(location):
            return self.run('rm -%sf %s && echo **OK** ; true' % (flag, location), showout=False)[1]

    def dir_ensure(self, location, recursive=True, mode=None, owner=None, group=None):
        """Ensures that there is a remote directory at the given location,
        optionally updating its mode / owner / group.

        If we are not updating the owner / group then this can be done as a single
        ssh call, so use that method, otherwise set owner / group after creation."""

        location = self.args_replace(location)
        if not self.dir_exists(location):
            self.run('mkdir %s %s' % (recursive and "-p" or "", location), showout=False)
        if owner or group or mode:
            self.dir_attribs(location, owner=owner, group=group, mode=mode, recursive=recursive)

        # make sure we redo these actions

    createDir = dir_ensure

    def fs_find(self, path, recursive=True, pattern="", findstatement="", type="", contentsearch="", extendinfo=False):
        """

        @param findstatement can be used if you want to use your own find arguments
        for help on find see http: // www.gnu.org / software / findutils / manual / html_mono / find.html

        @param pattern e.g. * / config / j*
            *   Matches any zero or more characters.
            ?   Matches any one character.
            [string] Matches exactly one character that is a member of the string string.

        @param type
            b    block(buffered) special
            c    character(unbuffered) special
            d    directory
            p    named pipe(FIFO)
            f    regular file
            l    symbolic link

        @param contentsearch
            looks for this content inside the files

        @param extendinfo: this will return [[$path, $sizeinkb, $epochmod]]
        """
        path = self.args_replace(path)
        cmd = "find %s" % path
        if recursive is False:
            cmd += " -maxdepth 1"
        # if contentsearch=="" and extendinfo==False:
        #     cmd+=" -print"
        if pattern != "":
            cmd += " -path '%s'" % pattern
        if contentsearch != "":
            type = "f"

        if type != "":
            cmd += " -type %s" % type

        if extendinfo:
            cmd += " -printf '%p||%k||%T@\n'"

        if contentsearch != "":
            cmd += " -print0 | xargs -r -0 grep -l '%s'" % contentsearch

        out = self.run(cmd, showout=False)[1]
        # print (cmd)
        self.logger.debug(cmd)

        paths = [item.strip() for item in out.split("\n") if item.strip() != ""]
        paths = [item for item in paths if item.startswith("+ find") is False]

        # print cmd

        paths2 = []
        if extendinfo:
            for item in paths:
                if item.find("||") != -1:
                    path, size, mod = item.split("||")
                    if path.strip() == "":
                        continue
                    paths2.append([path, int(size), int(float(mod))])
        else:
            paths2 = [item for item in paths if item.strip() != ""]

        return paths2

    # -----------------------------------------------------------------------------
    # CORE
    # -----------------------------------------------------------------------------

    def _clean(self, output):
        if self.sudomode and hasattr(self._executor, 'login'):
            dirt = '[sudo] password for %s: ' % self._executor.login
            if output.find(dirt) != -1:
                output = output.lstrip(dirt)
        return output

    def set_sudomode(self):
        self.sudomode = True

    def sudo(self, cmd, die=True, showout=True):
        sudomode = self.sudomode
        self.sudomode = True
        try:
            return self.run(cmd, die=die, showout=showout)
        finally:
            self.sudomode = sudomode

    def run(self, cmd, die=True, debug=None, checkok=False, showout=True, profile=False, replaceArgs=True,
            shell=False, env=None):
        """
        @param profile, execute the bash profile first
        """
        # print (cmd)
        if not env:
            env = {}
        if replaceArgs:
            cmd = self.args_replace(cmd)
        self._executor.curpath = self.cd
        # print ("CMD:'%s'"%cmd)
        if debug:
            debugremember = copy.copy(debug)
            self._executor.debug = debug

        if profile:
            ppath = self._cuisine.bash.profilePath
            if ppath:
                cmd = ". %s && %s" % (ppath, cmd)
            if showout:
                self.logger.info("PROFILECMD:%s" % cmd)
            else:
                self.logger.debug("PROFILECMD:%s" % cmd)

        if shell and '"' in cmd:
            cmd = cmd.replace('"', '\\"')

        if "cygwin" in self.uname:
            self.sudomode = False

        if self.sudomode:
            cmd = self.sudo_cmd(cmd, shell=shell)
        elif shell:  # only when shell is asked for
            cmd = 'bash -c "%s"' % cmd

        # old_path = self._executor.execute("echo $PATH", showout=False)[2]
        # if "/usr/local/bin" not in old_path:
        #     path = ['/usr/local/bin']
        #     path += [old_path] if old_path else []
        #     path += env.get("PATH", [])
        #     env = {"PATH": ":".join(path)}

        rc, out, err = self._executor.execute(cmd, checkok=checkok, die=False, showout=showout, env=env)

        out = self._clean(out)

        if rc > 0 and "brew unlink" in out and "To install this version" in out:
            from IPython import embed
            print("DEBUG NOW brew unlink")
            embed()
            raise RuntimeError("stop debug here")
            self._executor.execute("brew unlink ", checkok=checkok, die=False, showout=showout, env=env)

        # If command fails and die is true, raise error
        if rc and die:
            raise j.exceptions.RuntimeError('%s, %s' % (cmd, err))

        if debug:
            self._executor.debug = debugremember

        out = out.strip()

        return rc, out, err

    def sudo_cmd(self, command, shell=False, force_sudo=False):
        # TODO: Fix properly. This is just a workaround
        self.sudomode = False
        if "darwin" in self._cuisine.platformtype.osname:
            self.sudomode = True
            return command
        self.sudomode = True
        if not force_sudo and getattr(self._executor, 'login', '') == "root":
            cmd = command
        passwd = self._executor.passwd if hasattr(self._executor, "passwd") else ''
        passwd = passwd or "\'\'"
        if shell:
            command = 'bash -c "%s"' % command
        rc, out, err = self._executor.execute("which sudo", die=False, showout=False)
        if rc or out.strip() == '**OK**':
            # Install sudo if sudo not installed
            cmd = 'apt-get install sudo && echo %s | sudo -SE -p \'\' %s' % (passwd, command)
        else:
            cmd = 'echo %s | sudo -H -SE -p \'\' bash -c "%s"' % (passwd, command.replace('"', '\\"'))
        return cmd

    def cd(self, path):
        """cd to the given path"""
        path = self.args_replace(path)
        self.cd = path

    def pwd(self):
        return self.cd

    def execute_script(self, content, die=True, profile=False, interpreter="bash", tmux=True,
                       args_replace=True, showout=True):
        """
        generic exection of script, default interpreter is bash

        """
        if args_replace:
            content = self.args_replace(content)
        content = j.data.text.strip(content)

        self.logger.info("RUN SCRIPT:\n%s" % content)

        if content[-1] != "\n":
            content += "\n"

        if profile:
            ppath = self._cuisine.bash.profilePath
            if ppath:
                content = ". %s\n%s\n" % (ppath, content)

        if interpreter == "bash":
            content += "\necho '**OK**'\n"
        elif interpreter.startswith("python") or interpreter.startswith("jspython"):
            content += "\nprint('**OK**\\n')\n"

        ext = "sh"
        if interpreter.startswith("python"):
            ext = "py"
        elif interpreter.startswith("lua"):
            ext = "lua"

        rnr = j.data.idgenerator.generateRandomInt(0, 10000)
        path = "$tmpDir/%s.%s" % (rnr, ext)
        path = self.args_replace(path)

        if self.isMac:
            self.file_write(location=path, content=content, mode=0o770, showout=False)
        elif self.isCygwin:
            self.file_write(location=path, content=content, showout=False)
        else:
            self.file_write(location=path, content=content, mode=0o770, owner="root", group="root", showout=False)

        cmd = "%s %s" % (interpreter, path)

        if self.sudomode:
            cmd = self.sudo_cmd(cmd)

        cmd = "cd $tmpDir; %s" % (cmd, )
        cmd = self.args_replace(cmd)
        if tmux:
            rc, out = self._cuisine.tmux.executeInScreen("cmd", "cmd", cmd, wait=True, die=False)
            if showout:
                print(out)
        else:
            # outfile = "$tmpDir/%s.out" % (rnr)
            # outfile = self.cuisine.core.args_replace(outfile)
            # cmd = cmd + " 2>&1 || echo **ERROR** | tee %s" % outfile
            cmd = cmd + " 2>&1 || echo **ERROR**"
            rc, out, err = self._executor.executeRaw(cmd, showout=showout, die=False)
            out = out.rstrip().rstrip("\t")
            lastline = out.split("\n")[-1]
            if lastline.find("**ERROR**") != -1:
                if rc == 0:
                    rc = 1
            elif lastline.find("**OK**") != -1:
                rc = 0
            else:
                print(out)
                raise RuntimeError("wrong output of cmd")
            # out = self.file_read(outfile)
            out = self._clean(out)
            # self.file_unlink(outfile)
            out = out.replace("**OK**", "")
            out = out.replace("**ERROR**", "")
            out = out.strip()

        self.file_unlink(path)

        if rc > 0:
            msg = "Could not execute script:\n%s\n" % content
            msg += "Out/Err:\n%s\n" % out
            out = msg

            if die:
                raise j.exceptions.RuntimeError(out)

        return rc, out

    def execute_bash(self, script, die=True, profile=False, tmux=False, args_replace=True, showout=True):
        return self.execute_script(script, die=die, profile=profile, interpreter="bash", tmux=tmux,
                                   args_replace=args_replace, showout=showout)

    def execute_python(self, script, die=True, profile=False, tmux=False, args_replace=True, showout=True):
        return self.execute_script(script, die=die, profile=profile, interpreter="python3", tmux=tmux,
                                   args_replace=args_replace, showout=showout)

    def execute_jumpscript(self, script, die=True, profile=False, tmux=False, args_replace=True, showout=True):
        """
        execute a jumpscript(script as content) in a remote tmux command, the stdout will be returned
        """
        script = self.args_replace(script)
        script = j.data.text.strip(script)

        if script.find("from JumpScale import j") == -1:
            script = "from JumpScale import j\n\n%s" % script

        return self.execute_script(script, die=die, profile=profile, interpreter="jspython", tmux=tmux,
                                   args_replace=args_replace, showout=showout)

    # =============================================================================
    #
    # SHELL COMMANDS
    #
    # =============================================================================

    def command_check(self, command):
        """Tests if the given command is available on the system."""
        command = self.args_replace(command)
        rc, out, err = self.run("which '%s'" % command, die=False, showout=False, profile=True)
        return rc == 0

    def command_location(self, command):
        """
        return location of cmd
        """
        command = self.args_replace(command)
        return self._cuisine.bash.cmdGetPath(command)

    def command_ensure(self, command, package=None):
        """Ensures that the given command is present, if not installs the
        package with the given name, which is the same as the command by
        default."""
        command = self.args_replace(command)
        if package is None:
            package = command
        if not self.command_check(command):
            self._cuisine.package.install(package)
        assert self.command_check(command), \
            "Command was not installed, check for errors: %s" % (command)

    # SYSTEM IDENTIFICATION
    @property
    def _cgroup(self):
        def get():
            if self.isMac:
                return "none"
            return self.file_read("/proc/1/cgroup", "none")
        return self._cache.get("cgroup", get)

    @property
    def uname(self):
        if not hasattr(self, '_uname'):
            self._uname = self._executor.execute("uname -a", showout=False)[1].lower()
        return self._uname

    @property
    def isDocker(self):
        self._isDocker = self._cgroup.find("docker") != -1
        return self._isDocker

    @property
    def isLxc(self):
        self._isLxc = self._cgroup.find("lxc") != -1
        return self._isLxc

    @property
    def isUbuntu(self):
        return "ubuntu" in self._cuisine.platformtype.platformtypes

    @property
    def isArch(self):
        return "arch" in self._cuisine.platformtype.platformtypes

    @property
    def isMac(self):
        return "darwin" in self._cuisine.platformtype.platformtypes

    @property
    def isCygwin(self):
        return "cygwin" in self._cuisine.platformtype.platformtypes

    def __str__(self):
        return "cuisine:core:%s:%s" % (getattr(self._executor, 'addr', 'local'), getattr(self._executor, 'port', ''))

    __repr__ = __str__
