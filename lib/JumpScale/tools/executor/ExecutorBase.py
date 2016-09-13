from JumpScale import j


class ExecutorBase:

    def __init__(self, dest_prefixes={}, debug=False, checkok=False):

        self.dest_prefixes = dest_prefixes
        if "root" not in self.dest_prefixes:
            self.dest_prefixes["root"] = "/"
        if "tmp" not in self.dest_prefixes:
            self.dest_prefixes["tmp"] = "/tmp"
        if "code" not in self.dest_prefixes:
            self.dest_prefixes["code"] = "/opt/code"
        if "var" not in self.dest_prefixes:
            self.dest_prefixes["var"] = "%s/var" % j.do.BASE
        if "images" not in self.dest_prefixes:
            self.dest_prefixes["images"] = "/mnt/images"
        if "vm" not in self.dest_prefixes:
            self.dest_prefixes["vm"] = "/mnt/vm"

        self.debug = debug
        self.checkok = checkok
        self.logger = j.logger.get("j.tools.executor")
        self.env = {}
        self.curpath = ""
        self.platformtype = "linux"  # TODO: need to create propery and evaluate
        self.jumpscale = True  # TODO: need to create propery and evaluate
        self.id = None

        self._cuisine = None

    def checkplatform(self, name):
        """
        check if certain platform is supported
        e.g. can do check on unix, or linux, will check all
        """
        if name in j.core.platformtype.getParents(self.platformtype):
            return True
        return False

    def init(self):
        for key, val in self.dest_prefixes.items():
            self.execute("mkdir -p %s" % val)

    def docheckok(self, cmd, out):

        if out.find("**OK**") == -1:
            raise j.exceptions.RuntimeError("Error in:\n%s\n***\n%s" % (cmd, out))

    def _transformCmds(self, cmds, die=True, checkok=None):
        # print ("TRANSF:%s"%cmds)
        if cmds.find("\n") == -1:
            separator = ";"
        else:
            separator = "\n"

        pre = ""

        if checkok is None:
            checkok = self.checkok

        if die:
            if self.debug:
                if separator == ";":
                    pre += "set -x\n"
                else:
                    pre += "set -ex\n"
            else:
                if separator != ";":
                    pre += "set -e\n"

        if self.curpath != "":
            pre += "cd %s\n" % (self.curpath)

        if self.env != {}:
            for key, val in self.env.items():
                pre += "export %s='%s'\n" % (key, val)

        cmds = "%s\n%s" % (pre, cmds)

        if checkok:
            cmds += "\necho '**OK**'"

        cmds = cmds.replace("\n", separator).replace(";;", ";").strip(";")

        # print("DEBUG:%s"%self.debug)
        # print (cmds)
        # print ("***")

        return cmds

    @property
    def cuisine(self):
        if self._cuisine is None:
            self._cuisine = j.tools.cuisine.get(self)
            self._cuisine._executor = self
            try:
                self._cuisine.sshclient = self.sshclient
            except:
                pass
        return self._cuisine

    def exists(self, path):
        cuisine = self._cuisine or self.cuisine
        return self._cuisine.core.file_exists(path)
