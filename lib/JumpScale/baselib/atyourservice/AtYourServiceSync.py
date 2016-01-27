from JumpScale import j

class AtYourServiceSync():

    def __init__(self,sshport=22,rootpasswd="js111js",apikey="js111js"):
        self.nodes={}
        self.masters={}
        self.rootpasswd=rootpasswd
        self.apikey=apikey
        self.rootpasswd_master=rootpasswd
        self.apikey_master=apikey

    def installsync(self,name):
        node=self._getSyncClient(name)
        node.install()

    def installjs(self,ipaddr,sshport=22,docker=True,branch="master",dockerbase='/mnt/data/docker'):

        j.remote.ssh.fixsshConfigRemote(ipaddr,sshport=22)

        C="""
        cd /tmp;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh;bash install.sh        
        """

        if docker:
            C+="""
            ays install -n docker
            """

        #git to ssh
        C+="""
        apt-get install language-pack-en
        apt-get install make
        locale-gen

        ufw allow 22
        ufw enable &
        """

        #other way to do it
        #git remote set-url origin git@github.com:Jumpscale/jumpscale_core8.git

        C="""
        cd $codedir/github/jumpscale
        rm -rf jumpscale_core8/
        git clone git@github.com:Jumpscale/jumpscale_core8.git
        cd jumpscale_core8
        git fetch origin $branchname:$branchname
        git checkout $branchname
        git branch --set-upstream-to=origin/$branchname $branchname        
        cd ..

        set -ex
        cd $codedir/github/jumpscale
        rm -rf ays_jumpscale8/
        git clone git@github.com:Jumpscale/ays_jumpscale8.git
        cd ays_jumpscale8
        git fetch origin $branchname:$branchname
        git checkout $branchname
        git branch --set-upstream-to=origin/$branchname $branchname
        cd ..

        # """

        C=C.replace("$branchname",branch)
        C=C.replace("$dockerbase",dockerbase)
        C=C.replace("$codedir",j.do.CODEDIR)

        return j.do.executeBashScript(content=C, remote=ipaddr, sshport=sshport)

    def installmaster(self,name,installjs=True,docker=True,rootpasswd="js111js",apikey="js111js",):

        if installjs:
            res=self.installjs(name,branch=jsbranch,docker=docker)

        if docker:

            C="""
            ##web
            ufw allow 22001
            ##traffic
            ufw allow 22000
            ##udp announcments
            ufw allow 21025
            #ssh
            ufw allow 22022

            jsdocker new -n aysmaster -b despiegk/ubuntu1504 -p js007 --ports "22:22022 22001:22001 22000:22000 21025:21025" --start

            """
            res2=j.do.executeBashScript(content=C, remote=ipaddr, sshport=sshport)

        from IPython import embed
        print("DEBUG NOW mmmwss")
        embed()
        p
        



    def _getSyncClient(self,name):
        if name in self.master:
            node=self.master[name]
        elif name in self.nodes:
            node=self.nodes[name]
        else:
            raise RuntimeError("could not find node")


    def addNode(self, name,addr="localhost",sshport=22,port=22001):
        self.nodes[name]=j.clients.syncthing.get(addr=addr,port=port,sshport=sshport,rootpasswd=self.rootpasswd,apikey=self.apikey)

    def addMaster(self, name,addr="localhost",port=22001,sshport=22,rootpasswd="js111js",apikey="js111js"):

        self.nodes[name]=j.clients.syncthing.get(addr=addr,port=port,sshport=sshport,\
                rootpasswd=self.rootpasswd_master,apikey=self.apikey_master)


