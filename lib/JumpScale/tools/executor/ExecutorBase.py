from JumpScale import j

class ExecutorBase():

    def __init__(self,dest_prefixes={},debug=False,checkok=False):

        self.dest_prefixes=dest_prefixes
        if "root" not in self.dest_prefixes:
            self.dest_prefixes["root"]="/"
        if "tmp" not in self.dest_prefixes:
            self.dest_prefixes["tmp"]="/tmp"
        if "code" not in self.dest_prefixes:
            self.dest_prefixes["code"]="/opt/code"
        if "var" not in self.dest_prefixes:
            self.dest_prefixes["var"]="%s/var"%j.do.BASE
        if "images" not in self.dest_prefixes:
            self.dest_prefixes["images"]="/mnt/images"
        if "vm" not in self.dest_prefixes:
            self.dest_prefixes["vm"]="/mnt/vm"

        self.debug=debug
        self.checkok=checkok

        self.env = {}
        self.curpath = ""
        self.platformtype="linux" #@todo need to create propery and evaluate
        self.jumpscale=True #@todo need to create propery and evaluate

        self._cuisine=None

    def checkplatform(self,name):
        """
        check if certain platform is supported
        e.g. can do check on unix, or linux, will check all
        """
        if name in j.core.platformtype.getParents(self.platformtype):
            return True
        return False

    def init(self):
        for key,val in self.dest_prefixes.items():
            self.execute("mkdir -p %s"%val)

    def docheckok(self,cmd,out):
        
        if out.find("**OK**")==-1:
            raise RuntimeError("Error in:\n%s\n***\n%s"%(cmd,out))

    def _transformCmds(self, cmds, die=True,checkok=None):
        # print ("TRANSF:%s"%cmds)
        if cmds.find("\n") == -1:
            separator=";"
        else:
            separator="\n"

        pre=""

        if checkok==None:
            checkok=self.checkok

        if die:
            if self.debug:
                if separator==";":
                    pre+="set -x\n"
                else:
                    pre+="set -ex\n"
            else:
                if separator!=";":
                    pre+="set -e\n"

        if self.curpath!="":
            pre+="cd %s\n"%(self.curpath)

        if self.env!={}:
            for key,val in self.env.iteritems():
                pre+="export %s='%s'\n"%(self.curpath)


        cmds="%s\n%s"%(pre,cmds)

        if checkok:
            cmds+="\necho '**OK**'"

        cmds=cmds.replace("\n",separator).replace(";;",";").strip(";")

        # print("DEBUG:%s"%self.debug)
        # print (cmds)
        # print ("***")

        return cmds

    @property
    def cuisine(self):
        if self._cuisine==None:
            self._cuisine=j.tools.cuisine.get(self)
            self._cuisine.executor=self
            self._cuisine.sshclient=self.sshclient
        return self._cuisine
        