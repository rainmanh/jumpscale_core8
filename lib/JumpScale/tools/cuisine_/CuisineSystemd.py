
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

    def stop(self,name):
        cmd="systemctl disable %s"%name
        self.cuisine.run(cmd,showout=False)

        cmd="systemctl stop %s"%name
        self.cuisine.run(cmd,showout=False)

    def remove(self,prefix):
        for name,status in self.systemd.list(prefix):
            self.systemd.stop(name)
            for item in self.cuisine.fs_find("/etc/systemd",True,"*%s.service"%name):
                print("remove:%s"%item)
                self.cuisine.file_unlink(item)
        self.cuisine.run("systemctl daemon-reload")


    def ensure(self,name,cmd,descr="",systemdunit=""):
        """
        Ensures that the given systemd service is self.cuisine.running, starting
        it if necessary and also create it
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
        self.cuisine.run("systemctl enable %s"%name)
        self.cuisine.run("systemctl daemon-reload;systemctl restart %s"%name)

        

