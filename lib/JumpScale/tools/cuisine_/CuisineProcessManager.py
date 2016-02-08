
from JumpScale import j

class CuisineSystemd():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine


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

        self.cuisine.process.kill(name)

    def remove(self,prefix):
        for name,status in self.systemd.list(prefix):
            self.systemd.stop(name)
            for item in self.cuisine.fs_find("/etc/systemd",True,"*%s.service"%name):
                print("remove:%s"%item)
                self.cuisine.file_unlink(item)
        self.cuisine.run("systemctl daemon-reload")


    def ensure(self,name,cmd="",descr="",systemdunit=""):
        """
        Ensures that the given systemd service is self.cuisine.running, starting
        it if necessary and also create it
        @param systemdunit is the content of the file, will still try to replace the cmd
        """
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

class CuisineUpstart():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    
    def ensure(self,name, *args):
        """Ensures that the given upstart service is self.running, starting
        it if necessary."""
        status = self.cuisine.sudo("service %s status" % name,die=False)
        if status[0] == 3:
            status = self.cuisine.sudo("service %s start" % name)
        return status

    def reload(self,name, *args):
        """Reloads the given service, or starts it if it is not self.running."""
        status = self.cuisine.sudo("service %s reload" % name,die=False)
        if status[0] == 3:
            status = self.cuisine.sudo("service %s start" % name)
        return status

    def restart(self,name, *args):
        """Tries a `restart` command to the given service, if not successful
        will stop it and start it. If the service is not started, will start it."""
        status = self.cuisine.sudo("service %s status" % name,die=False)
        if status[0] == 3:
            return self.cuisine.sudo("service %s start" % name)
        else:
            status = self.cuisine.sudo("service %s restart" % name)
            if status[0] == 3:
                self.cuisine.sudo("service %s stop"  % name)
                return self.cuisine.sudo("service %s start" % name)
            else:
                return status
    def start(self, name, *args):
        status = self.cuisine.sudo("service %s status" % name,die=False)
        if status[0] == 3:
            return self.cuisine.sudo("service %s start" % name)
        else:
            return status


    def stop(self,name, *args):
        """Ensures that the given upstart service is stopped."""
        status = self.cuisine.sudo("service %s status" % name,die=False)
        if status[0] == 0:
            status = self.cuisine.sudo("service %s stop" % name)
        return status



        

