
from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineDocker(app):
    NAME = "docker"
    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def install(self):
        if self._cuisine.core.isUbuntu:
            if not self._cuisine.core.command_check('docker'):
                C = """
                wget -qO- https://get.docker.com/ | sh
                """
                self._cuisine.core.execute_bash(C)
            if not self._cuisine.core.command_check('docker-compose'):
                C = """
                curl -L https://github.com/docker/compose/releases/download/1.8.0-rc1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
                chmod +x /usr/local/bin/docker-compose
                """
                self._cuisine.core.execute_bash(C)
        if self._cuisine.core.isArch:
            self._cuisine.package.install("docker")
            self._cuisine.package.install("docker-compose")

    def ubuntuBuild(self, push=False):

        # TODO: *2 test

        dest = self._cuisine.development.git.pullRepo('https://github.com/Jumpscale/dockers.git', ssh=False)
        path = self._cuisine.core.joinpaths(dest, 'js8/x86_64/2_ubuntu1604')

        C = """
        set -ex
        cd %s
        docker build -t jumpscale/ubuntu1604 --no-cache .
        """ % path
        self._cuisine.core.execute_bash(C)

        if push:
            C = """
            set -ex
            cd %s
            docker push jumpscale/ubuntu1604
            """ % path
            self._cuisine.core.execute_bash(C)

    def resetPasswd(self, dockerCuisineObject):
        # change passwd
        dockerCuisineObject.user.passwd("root", j.data.idgenerator.generateGUID())

    def dockerStart(self, name="ubuntu1", image='jumpscale/ubuntu1604_all', ports=None, volumes=None, pubkey=None, weave=False):
        """
        will return dockerCuisineObj: is again a cuisine obj on which all kinds of actions can be executed

        @param ports e.g. 2022,2023
        @param volumes e.g. format: "/var/insidemachine:/var/inhost # /var/1:/var/1
        @param ports e.g. format "22:8022 80:8080"  the first arg e.g. 22 is the port in the container

        """
        # TODO: *1 test
        cmd = "jsdocker create --name {name} --image {image}".format(name=name, image=image)
        if pubkey:
            cmd += " --pubkey '%s'" % pubkey
        if ports:
            cmd += " --ports '%s'" % ports
        if volumes:
            cmd += " --volumes '%s'" % volumes
        # if aydofs:
        #     cmd += " --aysfs"
        self._cuisine.core.run(cmd, profile=True)
        cmd = "jsdocker list --name {name} --parsable".format(name=name)
        _, out, _ = self._cuisine.core.run(cmd, profile=True)
        info = j.data.serializer.json.loads(out)

        port = info[0]["port"]
        if 'host' in info[0]:
            host = info[0]['host']
            connstr = "%s:%s" % (host, port)
        else:
            connstr = "%s:%s" % (self._executor.addr, port)

        cuisinedockerobj = j.tools.cuisine.get(connstr)

        # TODO: *1 implement weave integration

        # TODO: *1 create ssh portforward from this cuisine to localhost to allow access to port used by this docker

        # NEED TO MAKE SURE WE CAN GET ACCESS TO THIS DOCKER WITHOUT OPENING PORTS
        # ON DOCKER HOST (which is current cuisine)

        return cuisinedockerobj

#
# def archBuild(self):
#     C = """
#     FROM base/archlinux:latest
#
#     MAINTAINER "Matthias Adler" <macedigital@gmail.com> / kristof de spiegeleer
#
#     RUN pacman -S --debug --noconfirm archlinux-keyring
#
#     RUN pacman -S --needed --noconfirm git iproute2 iputils procps-ng tar which licenses util-linux
#     RUN pacman -S --noconfirm curl wget ssh  mc
#
#
#     # remove unneeded pkgs, update and clean cache
#     # RUN pacman -Rss --noconfirm cronie device-mapper dhcpcd diffutils file nano vi texinfo usbutils gcc pinentry; \
#
#     # RUN pacman -Syu --force --noconfirm; pacman -Scc --noconfirm
#
#     # remove man pages and locale data
#     RUN rm -rf /archlinux/usr/share/locale && rm -rf /archlinux/usr/share/man
#
#     # clean unneeded services
#     RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == systemd-tmpfiles-setup.service ] || rm -f $i; done); \
#     rm -f /lib/systemd/system/multi-user.target.wants/*;\
#     rm -f /lib/systemd/system/graphical.target.wants/*; \
#     rm -f /etc/systemd/system/*.wants/*;\
#     rm -f /lib/systemd/system/local-fs.target.wants/*; \
#     rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
#     rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
#     rm -f /lib/systemd/system/basic.target.wants/*;\
#     rm -f /lib/systemd/system/anaconda.target.wants/*;
#
#     # switch default target from graphical to multi-user
#     RUN systemctl set-default multi-user.target
#
#     # systemd inside a container
#     ENV container docker
#     VOLUME [ "/sys/fs/cgroup" ]
#
#     CMD ["/usr/sbin/init"]
#
#     """
#     self._cuisine.core.run("rm -rf $tmpDir/docker;mkdir $tmpDir/docker")
#     self._cuisine.core.file_write("$tmpDir/docker/Dockerfile", C)
#
#     C = """
#     set -ex
#     cd $tmpDir/docker
#     docker build -t arch .
#     """
#     self._cuisine.core.execute_bash(C)
