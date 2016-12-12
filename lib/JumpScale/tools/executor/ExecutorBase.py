from JumpScale import j


class ExecutorBase:

    def __init__(self, dest_prefixes={}, debug=False, checkok=False):

        self.type = None
        self.id = None

        self.curpath = ""

        self.debug = debug
        self.checkok = checkok

        self._cuisine = None

    @property
    def done(self):
        if self.readonly == False:
            path = '%s/jumpscale_done.yaml' % self.env["TMPDIR"]
            if not self.cuisine.core.exists(path):
                return {}
            else:
                from IPython import embed
                print("DEBUG NOW ExecutorBase doneGet")
                embed()
                raise RuntimeError("stop debug here")
        else:
            # this to make sure works in readonly mode
            return {}

    def doneSet(self, key, val=True):
        if self.readonly == False:
            d = self.done
            d[key] = val
            path = '%s/jumpscale_done.yaml' % self.env["TMPDIR"]

            with open(path, 'w') as outfile:
                yaml.dump(d, outfile, default_flow_style=False)

    @property
    def env(self):
        """
        environment are kept in redis, to allow multiple instances to work together
        """
        from IPython import embed
        print("DEBUG NOW env executor")
        embed()
        raise RuntimeError("stop debug here")

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
        return self._cuisine.core.exists(path)
