from JumpScale import j

class JailFactory(object):

    def __init__(self):
        self.__jslocation__ = "j.tools.jail"
        self.redis=j.clients.redis.getByInstance('system')
        self.base="/opt/jsbox"
        if not j.sal.fs.exists(path=self.base):
            raise RuntimeError("Please install jsbox (sandbox install for jumpscale)")

    def prepareJSJail(self):
        """
        prepare system we can create jail environments for jumpscale
        """

        j.sal.process.execute("chmod -R o-rwx /opt")
        j.sal.process.execute("chmod -R o+r /usr")
        j.sal.process.execute("chmod -R o-w /usr")
        j.sal.process.execute("chmod -R o-w /etc")
        j.sal.process.execute("chmod -R o-rwx /home")
        j.sal.process.execute("chmod o-rwx /mnt")
        
        # j.sal.fs.chmod("/opt/code/jumpscale", 0o777)
        j.sal.fs.chown("/opt", "root")
        j.sal.process.execute("chmod 777 /opt")

        #SHOULD WE ALSO DO NEXT?
        # j.sal.fs.chmod("/opt/code", 0o700)
        j.sal.process.execute("chmod 700 /opt/code")
        
        # j.sal.process.execute("chmod 777 /opt/jumpscale")
        # j.sal.process.execute("chmod -R 777 /opt/jumpscale8/bin")
        # j.sal.process.execute("chmod -R 777 /opt/jumpscale8/lib")
        # j.sal.process.execute("chmod -R 777 /opt/jumpscale8/libext")
        # j.sal.process.execute("chmod 777 /opt/code")

        j.sal.process.execute("chmod 777 %s"%self.base)
        j.sal.process.execute("chmod 777 /home")

        logdir="/tmp/tmuxsessions"
        j.sal.fs.createDir(logdir)
        j.sal.process.execute("chmod 777 %s"%logdir)


    def _createJSJailEnv(self,user,secret):
        """
        create jumpscale jail environment for 1 user
        """
        self.killSessions(user)

        j.system.unix.addSystemUser(user,None,"/bin/bash","/home/%s"%user)
        j.tools.cuisine.local.user_ensure(name, passwd=None, home=None, uid=None, gid=None, shell=None, fullname=None, encrypted_passwd=True)
        j.system.unix.setUnixUserPassword(user,secret)
        j.sal.fs.copyDirTree("%s/apps/jail/defaultenv"%self.base,"/home/%s"%(user))
        j.sal.fs.symlink("%s/bin"%self.base,"/home/%s/jumpscale/bin"%(user))
        j.sal.fs.symlink("%s/lib"%self.base,"/home/%s/jumpscale/lib"%(user))
        j.sal.fs.symlink("%s/libext"%self.base,"/home/%s/jumpscale/libext"%(user))
        j.sal.fs.createDir("/home/%s/jumpscale/apps"%user)
        # j.sal.fs.symlink("/opt/code/jumpscale/default__jumpscale_examples/examples/","/home/%s/jumpscale/apps/examples"%user)
        # j.sal.fs.symlink("/opt/code/jumpscale/default__jumpscale_examples/prototypes/","/home/%s/jumpscale/apps/prototypes"%user)
        
        # def portals():
        #     j.sal.fs.symlink("/opt/code/jumpscale/default__jumpscale_portal/apps/portalbase/","/home/%s/jumpscale/apps/portalbase"%user)
        #     j.sal.fs.symlink("/opt/code/jumpscale/default__jumpscale_portal/apps/portalexample/","/home/%s/jumpscale/apps/portalexample"%user)
        #     src="/opt/code/jumpscale/default__jumpscale_grid/apps/incubaidportals/"
        #     j.sal.fs.copyDirTree(src,"/home/%s/jumpscale/apps/incubaidportals"%user)
        # portals()

        # src="/opt/code/jumpscale/default__jumpscale_lib/apps/cloudrobot/"
        # j.sal.fs.copyDirTree(src,"/home/%s/jumpscale/apps/cloudrobot"%user)

        # src="/opt/code/jumpscale/default__jumpscale_core/apps/admin/"
        # j.sal.fs.copyDirTree(src,"/home/%s/jumpscale/apps/admin"%user)

        j.sal.process.execute("chmod -R ug+rw /home/%s"%user)
        j.sal.fs.chown("/home/%s"%user, user)
        j.sal.process.execute("rm -rf /tmp/mc-%s"%user)

        secrpath="/home/%s/.secret"%user
        j.sal.fs.writeFile(filename=secrpath,contents=secret)

        j.sal.fs.writeFile("/etc/sudoers.d/%s"%user,"%s ALL = (root) NOPASSWD:ALL"%user)
        

    def listSessions(self,user):
        return j.sal.tmux.getSessions(user="user1")
        # res=[]
        # try:
        #     rc,out=j.sal.process.execute("sudo -i -u %s tmux list-sessions"%user)
        # except Exception,e:
        #     if str(e).find("Connection refused") != -1:
        #         return []
        #     print "Exception in listsessions:%s"%e
        #     return []
        # for line in out.split("\n"):
        #     if line.strip()=="":
        #         continue
        #     if line.find(":") != -1:
        #         name=line.split(":",1)[0].strip()
        #         res.append(name)
        # return res

    def killSessions(self,user):
        j.sal.process.killUserProcesses(user)
        j.sal.fs.removeDirTree("/home/%s"%user)        
        j.system.unix.removeUnixUser(user, removehome=True,die=False)
        user=user.strip()
        keys=self.redis.hkeys("robot:sessions")
        for key in keys:
            user2,session=key.split("__")
            if user==user2.strip():
                data=self.redis.hget("robot:sessions",key)
                session=j.data.serializer.json.loads(data)
                for pid in session["pids"]:
                    if j.sal.process.isPidAlive(pid):
                        j.sal.process.kill(pid)
                        # print "KILL %s"%pid
                self.redis.hdel("robot:sessions",key)
        
            
    def killAllSessions(self):
        for user in  j.sal.fs.listDirsInDir("/home",False,True):
            secrpath="/home/%s/.secret"%user
            if j.sal.fs.exists(path=secrpath):
                self.killSessions(user)
        cmd="killall shellinaboxd"
        j.sal.process.execute(cmd)

    def send2session(self,user,session,cmd):
        j.sal.process.execute("sudo -u %s -i tmux send -t %s %s ENTER"%(user,session,cmd))

    def createJSJailSession(self,user,secret,session,cmd=None):
        self._createJSJailEnv(user,secret)
        # secrpath="/home/%s/.secret"%user
        # secret=j.sal.fs.fileGetContents(secrpath).strip()

        #check session exists
        sessions=self.listSessions(user)
        if not session in sessions:
            #need to create session
            cmd="sudo -u %s -i tmux new-session -d -s %s"%(user,session)
            
            j.sal.process.execute(cmd)
            j.sal.process.execute("sudo -u %s -i tmux set-option -t %s status off"%(user,session))
            if cmd!=None:
                self.send2session(user,session,"clear")  


            

             
