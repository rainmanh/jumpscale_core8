
from JumpScale import j
# import os

# import socket

from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.docker"



class CuisineDocker():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    @actionrun(action=True)
    def install(self):
        self.cuisine.installer.docker()

    def archBuild(self): #@todo (*2*)
        C="""
        FROM base/archlinux:latest

        MAINTAINER "Matthias Adler" <macedigital@gmail.com> / kristof de spiegeleer

        RUN pacman -S --debug --noconfirm archlinux-keyring

        RUN pacman -S --needed --noconfirm git iproute2 iputils procps-ng tar which licenses util-linux
        RUN pacman -S --noconfirm curl wget ssh  mc


        # remove unneeded pkgs, update and clean cache
        # RUN pacman -Rss --noconfirm cronie device-mapper dhcpcd diffutils file nano vi texinfo usbutils gcc pinentry; \

        # RUN pacman -Syu --force --noconfirm; pacman -Scc --noconfirm

        # remove man pages and locale data
        RUN rm -rf /archlinux/usr/share/locale && rm -rf /archlinux/usr/share/man

        # clean unneeded services
        RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == systemd-tmpfiles-setup.service ] || rm -f $i; done); \
        rm -f /lib/systemd/system/multi-user.target.wants/*;\
        rm -f /lib/systemd/system/graphical.target.wants/*; \
        rm -f /etc/systemd/system/*.wants/*;\
        rm -f /lib/systemd/system/local-fs.target.wants/*; \
        rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
        rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
        rm -f /lib/systemd/system/basic.target.wants/*;\
        rm -f /lib/systemd/system/anaconda.target.wants/*;

        # switch default target from graphical to multi-user
        RUN systemctl set-default multi-user.target

        # systemd inside a container
        ENV container docker
        VOLUME [ "/sys/fs/cgroup" ]

        CMD ["/usr/sbin/init"]

        """
        self.cuisine.run("rm -rf $tmpDir/docker;mkdir $tmpDir/docker")
        self.cuisine.file_write("$tmpDir/docker/Dockerfile",C)

        C="""
        set -ex
        cd $tmpDir/docker
        docker build -t arch .
        """
        self.cuisine.run_script(C)

    def ubuntuBuild(self):

        dest = self.cuisine.git.pullRepo('https://github.com/Jumpscale/dockers.git', ssh=False)
        path = self.cuisine.joinpaths(dest, 'js8/x86_64/2_ubuntu1510')

        C="""
        set -ex
        cd %s
        docker build -t jumpscale/ubuntu1510 --no-cache .
        docker push jumpscale/ubuntu1510
        """ % path
        self.cuisine.run_script(C)

    @actionrun(action=True)
    def ubuntu(self, name="ubuntu1", image='jumpscale/ubuntu1510', ports=None, volumes=None, pubkey=None, aydofs=False):
        if not aydofs:
            cmd = "jsdocker create --name {name} --image {image}".format(name=name, image=image)
            if pubkey:
                cmd += " --pubkey '%s'" % pubkey
            if ports:
                cmd += " --ports '%s'" % ports
            if volumes:
                cmd += " --volumes '%s'" % volumes
            self.cuisine.run(cmd, profile=True)
            cmd = "jsdocker list --name {name} --parsable".format(name=name)
            out = self.cuisine.run(cmd, profile=True)
            info = j.data.serializer.json.loads(out)
            return info[0]['port']
        #TODO:
        #- start from docker repo where pushed docker image is (build using self.ubuntuBuild)
        #- mount over aydofs see docker_approach.md in this dir (improve jsdocker to also work with aydofs)
        #- put ssh key in place for mgmt (use jsdocker remote)
        #- return used port (jsdocker)

    @actionrun(action=True)
    def ubuntuSystemd(self,name="ubuntu1"):
        """
        start ubuntu 15.10 which is using systemd  #@todo (*2*)
        will have to do same tricks as with arch below
        """
        pass


    @actionrun(action=True)
    def ArchSystemd(self,name="arch1"):
        """
        start arch which is using systemd  #@todo (*2*) there is an issue with tty, cannot install anything (see in arch builder)
        """
        if not self.cuisine.isArch:
            raise RuntimeError("not supported")

        C="""

        set -ex
        mkdir -p /tmp2/
        chmod 600 /tmp2
        mkdir -p /tmp2/cgroup
        mkdir -p /tmp2/cgroup/systemd
        mount --bind /sys/fs/cgroup/systemd /tmp2/cgroup/systemd
        """
        self.cuisine.run_script(C)

        C="""
        set +ex
        docker kill $name
        docker rm $name

        set -ex
        mkdir -p /tmp2/$name/run
        mount -t tmpfs tmpfs /tmp2/$name/run

        mkdir -p /tmp2/$name/run/lock
        mount -t tmpfs tmpfs /tmp2/$name/run/lock

        """
        C=C.replace("$name",name)
        print (C)
        self.cuisine.run_script(C)

        # self.cuisine.run("docker run -d --name %s -v /tmp2/cgroup:/sys/fs/cgroup:ro -v /tmp2/%s/run:/run:rw tozd/ubuntu-systemd"%(name,name))
        self.cuisine.run("docker run -d --name %s -v /tmp2/cgroup:/sys/fs/cgroup:ro -v /tmp2/%s/run:/run:rw arch"%(name,name))
