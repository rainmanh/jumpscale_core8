
from JumpScale import j
import re
#we implemented a fallback system if systemd does not exist

class CuisineSystemd():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine
        self._systemdOK=None
        self.forceTMUX=False

    @property
    def systemdOK(self):
        if self._systemdOK==None:
            if self.forceTMUX:
                self._systemdOK=False
            else:
                self._systemdOK=self.cuisine.command_check("systemctl")
        return self._systemdOK


    def list(self,prefix=""):
        """
        @return [[$name,$status]]
        """
        if self.systemdOK:
            cmd='systemctl  --no-pager -l -t service list-unit-files'
            out=self.cuisine.run(cmd,showout=False)
            p = re.compile(u"(?P<name>[\S]*).service *(?P<state>[\S]*)")
            result=[]
            for line in out.split("\n"):
                res=re.search(p, line)
                if res!=None:
                    # print (line)
                    d=res.groupdict()
                    if d["name"].startswith(prefix):
                        result.append([d["name"],d["state"]])
        else:
            from IPython import embed
            print ("DEBUG NOW list tmux")
            embed()

        return result

    def reload(self):
        if self.systemdOK:
            self.cuisine.run("systemctl daemon-reload")

    def start(self,name):
        if self.systemdOK:
            self.reload()
            # self.cuisine.run("systemctl enable %s"%name,showout=False)
            self.cuisine.run("systemctl enable %s"%name,die=False,showout=False)
            cmd="systemctl restart %s"%name
            self.cuisine.run(cmd,showout=False)
        else:
            cmd=j.core.db.hget("processcmds",name).decode()
            self.stop(name)
            self.cuisine.tmux.executeInScreen("main", name, cmd, wait=True, reset=False)            

    def stop(self,name):
        if self.systemdOK:
            cmd="systemctl disable %s"%name
            self.cuisine.run(cmd,showout=False,die=False)

            cmd="systemctl stop %s"%name
            self.cuisine.run(cmd,showout=False,die=False)
        else:
            self.cuisine.tmux.killWindow("main",name)            

    def remove(self,prefix):
        for name,status in self.list(prefix):
            cmd=j.core.db.hdel("processcmds",name)
            self.stop(name)
            if self.systemdOK:
                for item in self.cuisine.fs_find("/etc/systemd",True,"*%s.service"%name):
                    print("remove:%s"%item)
                    self.cuisine.file_unlink(item)
                self.cuisine.run("systemctl daemon-reload")

    def ensure(self,name,cmd="",env={},path="",descr="",systemdunit=""):
        """
        Ensures that the given systemd service is self.cuisine.running, starting
        it if necessary and also create it
        @param systemdunit is the content of the file, will still try to replace the cmd
        """

        cmd=self.cuisine.args_replace(cmd)
        path=self.cuisine.args_replace(path)
        #need to remember for future usage
        if cmd=="":
            cmd=j.core.db.hget("processcmds",name).decode()
        else:
            #find absolute path
            if self.systemdOK:
                if not cmd.startswith("/"):
                    cmd0=cmd.split(" ",1)[0]
                    cmd1=self.cuisine.bash.cmdGetPath(cmd0)
                    cmd=cmd.replace(cmd0,cmd1)

            envstr = ""
            for name0, value in list(env.items()):
                envstr += "export %s=%s\n" % (name0, value)

            if envstr!="":
                cmd="%s;%s"%(envstr,cmd)

            cmd = cmd.replace('"', r'\"')

            if path:
                cwd = "cd %s;" % path
                if not cmd.startswith("."):
                    cmd="./%s"%cmd
                cmd = "%s %s" % (cwd, cmd)

            j.core.db.hset("processcmds",name,cmd)

        if self.systemdOK:

            if systemdunit!="":
                C=systemdunit
            else:
                C="""
                [Unit]
                Description=$descr
                Wants=network-online.target
                After=network-online.target

                [Service]
                ExecStart=$cmd
                Restart=always

                [Install]
                WantedBy=multi-user.target
                """
            C=C.replace("$cmd",cmd)
            if descr=="":
                descr=name
            C=C.replace("$descr",descr)

            self.cuisine.file_write("/etc/systemd/system/%s.service"%name,C)

            self.cuisine.run("systemctl daemon-reload;systemctl restart %s"%name)
            self.cuisine.run("systemctl enable %s"%name,die=False,showout=False)
            self.cuisine.run("systemctl daemon-reload;systemctl restart %s"%name)

        
        else:
            self.start(name)
            
    def startAll(self):
        if self.systemdOK:
            #@todo (*1*) start all cuisine services
            raise RuntimeError("not implemented, please do")
        else:            
            for key in j.core.db.hkeys("processcmds"):
                key=key.decode()
                cmd=j.core.db.hget("processcmds",key).decode()
                self.start(key)


