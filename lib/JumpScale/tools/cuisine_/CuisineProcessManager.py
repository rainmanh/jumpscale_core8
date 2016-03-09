from JumpScale import j
import time
import re

#not using cuisine.tmux.executeInScreen
class ProcessManagerBase:

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    def get(self, pm = None):
        from ProcessManagerFactory import ProcessManagerFactory
        return ProcessManagerFactory(self.cuisine).get(pm)

class CuisineSystemd(ProcessManagerBase):
    def __init__(self,executor,cuisine):
        super().__init__(executor, cuisine)

    def list(self,prefix=""):
        """
        @return [[$name,$status]]
        """

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

        return result

    def reload(self):
        self.cuisine.run("systemctl daemon-reload")

    def start(self,name):
        self.reload()
        # self.cuisine.run("systemctl enable %s"%name,showout=False)
        self.cuisine.run("systemctl enable %s"%name,die=False,showout=False)
        cmd="systemctl restart %s"%name
        self.cuisine.run(cmd,showout=False)



    def stop(self,name):
            cmd="systemctl disable %s"%name
            self.cuisine.run(cmd,showout=False,die=False)

            cmd="systemctl stop %s"%name
            self.cuisine.run(cmd,showout=False,die=False)


    def remove(self,prefix):
        self.stop(prefix)
        for name,status in self.list(prefix):
            self.stop(name)

            for item in self.cuisine.fs_find("/etc/systemd",True,"*%s.service"%name):
                print("remove:%s"%item)
                self.cuisine.file_unlink(item)
            self.cuisine.run("systemctl daemon-reload")

    def ensure(self,name,cmd="",env={},path="",descr="",systemdunit="", **kwargs):
        """
        Ensures that the given systemd service is self.cuisine.running, starting
        it if necessary and also create it
        @param systemdunit is the content of the file, will still try to replace the cmd
        """

        if not path:
            path = '/root'
        cmd = self.cuisine.args_replace(cmd)
        path = self.cuisine.args_replace(path)
        if cmd != "":
            if not cmd.startswith("/"):
                cmd0=cmd.split(" ",1)[0]
                cmd1=self.cuisine.bash.cmdGetPath(cmd0)
                cmd=cmd.replace(cmd0,cmd1)

            envstr = ""
            for name0, value in list(env.items()):
                envstr += "%s=%s " % (name0, value)

            cmd = self.cuisine._clean(cmd)

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
                WorkingDirectory=$cwd
                Environment=$env

                [Install]
                WantedBy=multi-user.target
                """
            C=C.replace("$cmd", cmd)
            C=C.replace("$cwd", path)
            C=C.replace("$env", envstr)
            if descr=="":
                descr=name
            C=C.replace("$descr",descr)

            self.cuisine.file_write("/etc/systemd/system/%s.service"%name,C)

            self.cuisine.run("systemctl daemon-reload;systemctl restart %s"%name)
            self.cuisine.run("systemctl enable %s"%name,die=False,showout=False)
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


class CuisineRunit(ProcessManagerBase):
    def __init__(self,executor,cuisine):
        super().__init__(executor, cuisine)

    def list(self,prefix=""):
        result = list()

        for service in self.cuisine.fs_find("/etc/service/", recursive=False)[1:]:
            service = service.split("/etc/service/")[1]
            status = self.cuisine.run("sv  status /etc/service/%s" %service).split(":")[0]
            result.append([service, status])
        return result

    def ensure(self, name, cmd="", env={}, path="", descr=""):
        """Ensures that the given upstart service is self.running, starting
        it if necessary."""

        if not self.cuisine.file_exists("/etc/service/vice/%s/run" %name ):
            cmd=self.cuisine.args_replace(cmd)
            path=self.cuisine.args_replace(path)


            envstr = ""
            for name0, value in list(env.items()):
                envstr += "export %s=%s\n" % (name0, value)


            if path and (path not in cmd):
                cmd = "%s/%s" % (path, cmd)

            sv_text ="""#!/bin/sh
set -e
echo $descrs
$env
cd $path
exec $cmd
            """
            sv_text = sv_text.replace("$env", envstr)
            sv_text = sv_text.replace("$path", path)
            sv_text = sv_text.replace("$cmd",cmd)
            if descr=="":
                descr = name
            sv_text = sv_text.replace("$descr",descr)
            sv_text = sv_text.replace("$path",path)

            # if self.cuisine.file_is_link("/etc/service/"):
            #     self.cuisine.file_link( "/etc/getty-5", "/etc/service")
            self.cuisine.file_ensure("/etc/service/%s/run" %name,mode="+x")
            self.cuisine.file_write("/etc/service/%s/run" %name, sv_text)
            time.sleep(5)

        self.start(name)

    def remove(self, prefix):
        """removes process from init"""
        if self.cuisine.file_exists("/etc/service/%s/run" %prefix ):
            self.stop(prefix)
            self.cuisine.dir_remove("/etc/service/%s/run" %prefix)




    def reload(self, name):
        """Reloads the given service, or starts it if it is not self.running."""
        if self.cuisine.file_exists("/etc/service/%s/run" %name ):
            self.cuisine.run("sv reload %s" %name, profile=True)


    def start(self, name):
        """Tries a `restart` command to the given service, if not successful
        will stop it and start it. If the service is not started, will start it."""
        if self.cuisine.file_exists("/etc/service/vice/%s/run" %name ):
            self.cuisine.run("sv -w 15 start /etc/service/%s/" %name, profile=True )

    def stop(self, name, **kwargs):
        """Ensures that the given upstart service is stopped."""
        if self.cuisine.file_exists("/etc/service/%s/run" %name):
            self.cuisine.run("sv -w 15 stop /etc/service/%s/" %name, profile=True)

class CuisineTmuxec(ProcessManagerBase):
    def __init__(self,executor,cuisine):
        super().__init__(executor, cuisine)

    def list(self,prefix=""):
        try:
            result = self.cuisine.run("tmux lsw", profile=True).split("\n")
        except:
            print("no running processes")
            return
        return result 
        
    def ensure(self, name, cmd="", env={}, path="", descr=""):
        """Ensures that the given upstart service is self.running, starting
        it if necessary."""
        cmd=self.cuisine.args_replace(cmd)
        path=self.cuisine.args_replace(path)

        if cmd=="":
            cmd=j.core.db.hget("processcmds",name).decode()
        else:
            envstr = ""
            for name0, value in list(env.items()):
                envstr += "export %s=%s && " % (name0, value)



            if path:
                cwd = "cd %s &&" % path
                cmd = "%s %s" % (cwd, cmd)
            if envstr!="":
                cmd="%s%s"%(envstr,cmd)

            j.core.db.hset("processcmds",name,cmd)

        self.stop(name)
        self.cuisine.tmux.createWindow("main", name)
        self.cuisine.tmux.executeInScreen("main", name, cmd)

    def reload(self, name):
        """Reloads the given service, or star
ts it if it is not self.running."""
        cmd=j.core.db.hget("processcmds",name).decode()
        self.stop(name)
        self.cuisine.tmux.executeInScreen("main", name,cmd=cmd)

    def start(self, name):
        """Tries a `restart` command to the given service, if not successful
        will stop it and start it. If the service is not started, will start it."""
        cmd=j.core.db.hget("processcmds",name).decode()
        self.stop(name)
        self.cuisine.tmux.executeInScreen("main", name,cmd=cmd)


    def stop(self, name):
        """Ensures that the given upstart service is stopped."""
        if name in self.list():
            pid = self.cuisine.tmux.getPid('main', name)
            self.cuisine.run("kill -9 %s" % pid)
            self.cuisine.tmux.killWindow("main",name)

    def remove(self, name):
        """removes service """
        if name in self.list():
            pid = self.cuisine.tmux.getPid('main', name)
            self.cuisine.run("kill -9 %s" % pid)
            self.cuisine.tmux.killWindow("main",name)
            j.core.db.hdel("processcmds",name)

