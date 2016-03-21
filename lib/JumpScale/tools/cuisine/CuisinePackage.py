
from JumpScale import j


from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.package"


class CuisinePackage():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    
    def _repository_ensure_apt(self,repository):
        self.ensure('python-software-properties')
        self.cuisine.core.sudo("add-apt-repository --yes " + repository)

    def _apt_get(self,cmd):
        CMD_APT_GET = 'DEBIAN_FRONTEND=noninteractive apt-get -q --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" '
        cmd    = CMD_APT_GET + cmd
        result = self.cuisine.core.sudo(cmd)
        # If the installation process was interrupted, we might get the following message
        # E: dpkg was interrupted, you must manually self.cuisine.core.run 'sudo dpkg --configure -a' to correct the problem.
        if "sudo dpkg --configure -a" in result:
            self.cuisine.core.sudo("DEBIAN_FRONTEND=noninteractive dpkg --configure -a")
            result = self.cuisine.core.sudo(cmd)
        return result

    @actionrun(action=True)
    def update(self,package=None):
        if self.cuisine.core.isUbuntu:
            if package == None:
                return self._apt_get("-q --yes update")
            else:
                if type(package) in (list, tuple):
                    package = " ".join(package)
                return self._apt_get(' upgrade ' + package)
        else:
            raise RuntimeError("could not install:%s, platform not supported"%package)

    @actionrun(action=True)
    def mdupdate(self):
        """
        update metadata of system
        """
        print ("packages mdupdate")
        if self.cuisine.core.isUbuntu:
            self.cuisine.core.run("apt-get update")
        elif self.cuisine.core.isMac:
            self.cuisine.core.run("brew update")
        elif self.cuisine.core.isArch:
            self.cuisine.core.run("pacman -Syy")

    @actionrun(action=True)
    def upgrade(self,distupgrade=False):
        """
        upgrades system, distupgrade means ubuntu 14.04 will fo to e.g. 15.04
        """
        self.mdupdate()
        print ("packages upgrade")
        if self.cuisine.core.isUbuntu:
            if distupgrade:
                return self._apt_get("dist-upgrade")
            else:
                return self._apt_get("upgrade")
        elif self.cuisine.core.isArch:
            self.cuisine.core.run("pacman -Syu --noconfirm;pacman -Sc --noconfirm")
        elif self.cuisine.core.isMac:
            self.cuisine.core.run("brew upgrade")
        else:
            raise RuntimeError("could not upgrade, platform not supported")

    @actionrun(action=True)
    def install(self,package):

        if self.cuisine.core.isUbuntu:
            cmd="apt-get install %s -y"%package

        elif self.cuisine.core.isArch:
            if package.startswith("python3"):
                package="extra/python"

            #ignore
            if package in ["libpython3.5-dev","libffi-dev","build-essential","libpq-dev","libsqlite3-dev"]:
                return

            cmd="pacman -S %s  --noconfirm"%package

        elif self.cuisine.core.isMac:

            rc,out=self.cuisine.core.run("brew info --json=v1 %s"%package,showout=False,die=False)
            if rc==0:
                info=j.data.serializer.json.loads(out)
                return #means was installed

            cmd="brew install %s "%package

        else:
            raise RuntimeError("could not install:%s, platform not supported"%package)

        mdupdate=False
        while True:
            rc,out=self.cuisine.core.run(cmd,die=False)  

            if rc>0:
                if mdupdate==True:
                    raise RuntimeError("Could not install:'%s' \n%s"%(package,out))


                if out.find("not found")!=-1 or out.find("failed to retrieve some files")!=-1:
                    self.mdupdate()
                    mdupdate=True
                    continue

                raise RuntimeError("Could not install:%s %s"%(package,out))

            return out


    def multiInstall(self,packagelist):
        """
        @param packagelist is text file and each line is name of package

        e.g.
            # python
            mongodb

        @param runid, if specified actions will be used to execute
        """
        for dep in packagelist.split("\n"):
            dep=dep.strip()
            if dep.strip()=="":
                continue
            if dep.strip()[0]=="#":
                continue
            dep=dep.strip()    
            if dep==None or dep=="":
                continue        
            self.install(dep)

    @actionrun()
    def start(self,package):        
        if self.cuisine.core.isArch or self.cuisine.core.isUbuntu or self.cuisine.core.isMac:
            self.cuisine.processmanager.start(package)    
        else:
            raise RuntimeError("could not install/ensure:%s, platform not supported" %package)           

    @actionrun(action=True)
    def ensure(self,package, update=False):
        """Ensure apt packages are installed"""
        if self.cuisine.core.isUbuntu:
            if isinstance(package, str):
                package = package.split()
            res = {}
            for p in package:
                p = p.strip()
                if not p: continue
                # The most reliable way to detect success is to use the command status
                # and suffix it with OK. This won't break with other locales.
                status = self.cuisine.core.run("dpkg-query -W -f='${Status} ' %s && echo **OK**;true" % p)
                if not status.endswith("OK") or "not-installed" in status:
                    self.install(p)
                    res[p]=False
                else:
                    if update:
                        self.update(p)
                    res[p]=True
            if len(res) == 1:
                for _, value in res.items():
                    return value
            else:
                return res
        elif self.cuisine.core.isArch:
            self.cuisine.core.run("pacman -S %s"%package)
        else:
            raise RuntimeError("could not install/ensure:%s, platform not supported"%package)            

        raise RuntimeError("not supported platform")

    @actionrun(action=True)
    def clean(self,package=None,agressive=False):
        """
        clean packaging system e.g. remove outdated packages & caching packages
        @param agressive if True will delete full cache

        """
        if self.cuisine.core.isUbuntu:
            if package!=None:
                return self._apt_get("-y --purge remove %s" % package)
            else:
                self.cuisine.core.run("apt-get autoremove -y")
        elif self.cuisine.core.isArch:
            cmd="pacman -Sc"
            if agressive:
                cmd+="c"
            self.cuisine.core.run(cmd)
            if aggressive:
                self.cuisine.core.run("pacman -Qdttq",showout=False)
        elif self.cuisine.core.isMac:
            pass
        else:
            raise RuntimeError("could not package clean:%s, platform not supported"%package)                       

    @actionrun(action=True)
    def remove(self,package, autoclean=False):
        if self.cuisine.core.isUbuntu:
            self._apt_get('remove ' + package)
            if autoclean:
                self._apt_get("autoclean")
        elif self.isMac:
            self.cuisine.core.run("pacman -Rs %s"%package)

    def __repr__(self):
        return "cuisine.package:%s:%s"%(self.executor.addr,self.executor.port)

    __str__=__repr__