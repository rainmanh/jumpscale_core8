
from JumpScale import j
import crypt


def shell_safe( path ):
    SHELL_ESCAPE            = " '\";`|"
    """Makes sure that the given path/string is escaped and safe for shell"""
    path= "".join([("\\" + _) if _ in SHELL_ESCAPE else _ for _ in path])
    return path



class CuisineUser():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine



    def passwd(self, name, passwd, encrypted_passwd=False):
        """Sets the given user password."""
        print("set user:%s passwd for %s"%(name,self))
        name = name.strip()
        passwd = passwd.strip()

        encoded_password = crypt.crypt(passwd)
        if encrypted_passwd:
            self.cuisine.sudo("usermod -p '%s' %s" % (encoded_password, name))
        else:
            # NOTE: We use base64 here in case the password contains special chars
            # TODO: Make sure this openssl command works everywhere, maybe we should use a text_base64_decode?
            # self.cuisine.sudo("echo %s | openssl base64 -A -d | chpasswd" % (shell_safe(encoded_password)))
            # self.cuisine.sudo("echo %s | openssl base64 -A -d | chpasswd" % (encoded_password))
            self.cuisine.run("echo \"%s:%s\" | chpasswd"%(name, passwd))
        #executor = j.tools.executor.getSSHBased(self.executor.addr, self.executor.port, name, passwd, checkok=True)


    def create(self,name, passwd=None, home=None, uid=None, gid=None, shell=None,
        uid_min=None, uid_max=None, encrypted_passwd=True, fullname=None, createhome=True):
        """Creates the user with the given name, optionally giving a
        specific password/home/uid/gid/shell."""

        name=name.strip()
        passwd=passwd.strip()
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
        self.cuisine.sudo("useradd %s '%s'" % (" ".join(options), name))
        if passwd:
            self.passwd(name=name,passwd=passwd,encrypted_passwd=encrypted_passwd)

    def check(self,name=None, uid=None, need_passwd=True):
        """Checks if there is a user defined with the given name,
        returning its information as a
        '{"name":<str>,"uid":<str>,"gid":<str>,"home":<str>,"shell":<str>}'
        or 'None' if the user does not exists.
        need_passwd (Boolean) indicates if password to be included in result or not.
            If set to True it parses 'getent shadow' and needs self.cuisine.sudo access
        """
        assert name!=None or uid!=None,     "check: either `uid` or `name` should be given"
        assert name is None or uid is None,"check: `uid` and `name` both given, only one should be provided"
        if name != None:
            d = self.cuisine.run("getent passwd | egrep '^%s:' ; true" % (name))
        elif uid != None:
            d = self.cuisine.run("getent passwd | egrep '^.*:.*:%s:' ; true" % (uid))
        results = {}
        s = None
        if d:
            d = d.split(":")
            assert len(d) >= 7, "passwd entry returned by getent is expected to have at least 7 fields, got %s in: %s" % (len(d), ":".join(d))
            results = dict(name=d[0], uid=d[2], gid=d[3], fullname=d[4], home=d[5], shell=d[6])
            if need_passwd:
                s = self.cuisine.sudo("getent shadow | egrep '^%s:' | awk -F':' '{print $2}'" % (results['name']))
                if s: results['passwd'] = s
        if results:
            return results
        else:
            return None

    def ensure(self,name, passwd=None, home=None, uid=None, gid=None, shell=None, fullname=None, encrypted_passwd=True,group=None):
        """Ensures that the given users exists, optionally updating their
        passwd/home/uid/gid/shell."""
        d = self.check(name)
        if not d:
            self.create(name, passwd, home, uid, gid, shell, fullname=fullname, encrypted_passwd=encrypted_passwd)
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
                self.cuisine.sudo("usermod %s '%s'" % (" ".join(options), name))
            if passwd:
                self.passwd(name=name, passwd=passwd, encrypted_passwd=encrypted_passwd)
        if group!=None:
            self.cuisine.group.user_add(group=group, user=name)


    def remove(self,name, rmhome=None):
        """Removes the user with the given name, optionally
        removing the home directory and mail spool."""
        options = ["-f"]
        if rmhome:
            options.append("-r")
        self.cuisine.sudo("userdel %s '%s'" % (" ".join(options), name))


    def list(self):
        users=self.fs_find("/home",recursive=False)
        users=[j.do.getBaseName(item) for item in users if (item.strip()!="" and item.strip("/")!="home")]
        return users
