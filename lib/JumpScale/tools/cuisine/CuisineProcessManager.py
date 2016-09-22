from JumpScale import j
import time
import re

# not using cuisine.tmux.executeInScreen
base = j.tools.cuisine._getBaseClass()


class ProcessManagerBase(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine
        self.logger = j.logger.get('j.tools.cuisine.processmanager')

    def exists(self, name):
        return name in self.list()

    def restart(self):
        self.stop()
        self.start()

    def reload(self):
        return self.restart()

    def get(self, pm=None):
        from .ProcessManagerFactory import ProcessManagerFactory
        return ProcessManagerFactory(self._cuisine).get(pm)


class CuisineSystemd(ProcessManagerBase):

    def __init__(self, executor, cuisine):
        super().__init__(executor, cuisine)

    def list(self, prefix=""):
        """
        @return [$name]
        """
        cmd = 'systemctl  --no-pager -l -t service list-unit-files'
        out = self._cuisine.core.run(cmd, showout=False)[1]
        p = re.compile(u"(?P<name>[\S]*).service *(?P<state>[\S]*)")
        result = []
        for line in out.split("\n"):
            res = re.search(p, line)
            if res is not None:
                # print (line)
                d = res.groupdict()
                if d["name"].startswith(prefix):
                    result.append(d["name"])
        return result

    def reload(self):
        self._cuisine.core.run("systemctl daemon-reload")

    def start(self, name):
        self.reload()
        # self._cuisine.core.run("systemctl enable %s"%name,showout=False)
        self._cuisine.core.run("systemctl enable %s" % name, die=False, showout=False)
        cmd = "systemctl restart %s" % name
        self._cuisine.core.run(cmd, showout=False)

    def stop(self, name):
        cmd = "systemctl disable %s" % name
        self._cuisine.core.run(cmd, showout=False, die=False)

        cmd = "systemctl stop %s" % name
        self._cuisine.core.run(cmd, showout=False, die=False)
        self._cuisine.process.kill(name, signal=9, exact=False)

    def remove(self, prefix):
        self.stop(prefix)
        for name in self.list(prefix):
            self.stop(name)

            for item in self._cuisine.core.fs_find("/etc/systemd", True, "*%s.service" % name):
                print("remove:%s" % item)
                self._cuisine.core.file_unlink(item)

            for item in self._cuisine.core.fs_find("/etc/init.d", True, "*%s" % name):
                print("remove:%s" % item)
                self._cuisine.core.file_unlink(item)

            self._cuisine.core.run("systemctl daemon-reload")

    def ensure(self, name, cmd, env={}, path="", descr="", systemdunit="", **kwargs):
        """
        Ensures that the given systemd service is self._cuisine.core.running, starting
        it if necessary and also create it
        @param systemdunit is the content of the file, will still try to replace the cmd
        """

        if not path:
            path = '/root'
        cmd = self._cuisine.core.args_replace(cmd)
        path = self._cuisine.core.args_replace(path)

        if not cmd.startswith("/"):
            cmd0 = cmd.split(" ", 1)[0]
            cmd1 = self._cuisine.bash.cmdGetPath(cmd0)
            cmd = cmd.replace(cmd0, cmd1)

        envstr = ""
        for name0, value in list(env.items()):
            envstr += "%s=%s " % (name0, value)

        cmd = self._cuisine.core._clean(cmd)

        if systemdunit != "":
            C = systemdunit
        else:
            C = """
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
        C = C.replace("$cmd", cmd)
        C = C.replace("$cwd", path)
        C = C.replace("$env", envstr)
        if descr == "":
            descr = name
        C = C.replace("$descr", descr)

        self._cuisine.core.file_write("/etc/systemd/system/%s.service" % name, C)

        self._cuisine.core.run("systemctl daemon-reload;systemctl restart %s" % name)
        self._cuisine.core.run("systemctl enable %s" % name, die=False, showout=False)
        self.start(name)


class CuisineRunit(ProcessManagerBase):

    def __init__(self, executor, cuisine):
        super().__init__(executor, cuisine)
        self.timeout = 30

    def list(self, prefix=""):
        result = list()

        for service in self._cuisine.core.fs_find("/etc/service/", recursive=False)[1:]:
            service = service.split("/etc/service/")[1]
            status = self._cuisine.core.run("sv  status /etc/service/%s" % service)[1].split(":")[0]
            result.append(service)
        return result

    def ensure(self, name, cmd, env={}, path="", descr=""):
        """Ensures that the given upstart service is self.running, starting
        it if necessary."""

        cmd = self._cuisine.core.args_replace(cmd)
        path = self._cuisine.core.args_replace(path)

        envstr = ""
        for name0, value in list(env.items()):
            envstr += "export %s=%s\n" % (name0, value)

        sv_text = """#!/bin/sh
        set -e
        echo $descrs
        $env
        cd $path
        exec $cmd
        """
        sv_text = sv_text.replace("$env", envstr)
        sv_text = sv_text.replace("$path", path)
        sv_text = sv_text.replace("$cmd", cmd)
        if descr == "":
            descr = name
        sv_text = sv_text.replace("$descr", descr)
        sv_text = sv_text.replace("$path", path)

        # if self._cuisine.core.file_is_link("/etc/service/"):
        #     self._cuisine.core.file_link( "/etc/getty-5", "/etc/service")
        self._cuisine.core.file_ensure("/etc/service/%s/run" % name, mode="+x")
        self._cuisine.core.file_write("/etc/service/%s/run" % name, sv_text)

        # waiting for runsvdir to populate service directory monitor
        remain = 300
        while not self._cuisine.core.dir_exists("/etc/service/%s/supervise" % name):
            remain = remain - 1
            if remain == 0:
                self.logger.warn(
                    '/etc/service/%s/supervise: still not exists, check if runsvdir is running, start may fail.' % name)
                break

            time.sleep(0.2)

        self.start(name)

    def remove(self, prefix):
        """removes process from init"""
        if self._cuisine.core.file_exists("/etc/service/%s/run" % prefix):
            self.stop(prefix)
            self._cuisine.core.dir_remove("/etc/service/%s/run" % prefix)

    def reload(self, name):
        """Reloads the given service, or starts it if it is not self.running."""
        if self._cuisine.core.file_exists("/etc/service/%s/run" % name):
            self._cuisine.core.run("sv reload %s" % name, profile=True)

    def start(self, name):
        """Tries a `restart` command to the given service, if not successful
        will stop it and start it. If the service is not started, will start it."""
        if self._cuisine.core.file_exists("/etc/service/%s/run" % name):
            if name == 'redis_main':
                self.timeout = 60
            self._cuisine.core.run("sv -w %d start /etc/service/%s/" % (self.timeout, name), profile=True)

    def stop(self, name, **kwargs):
        """Ensures that the given upstart service is stopped."""
        if self._cuisine.core.file_exists("/etc/service/%s/run" % name):
            self._cuisine.core.run("sv -w %d stop /etc/service/%s/" % (self.timeout, name), profile=True)
        self._cuisine.process.kill(name, signal=9, exact=False)


class CuisineTmuxec(ProcessManagerBase):

    def __init__(self, executor, cuisine):
        super().__init__(executor, cuisine)

    def list(self, prefix=""):
        self._cuisine.package.install('tmux')

        rc, result, err = self._cuisine.core.run("tmux lsw 2> /dev/null || true", profile=True, die=False)
        if err:
            return []
        res = result.splitlines()
        res = [item.split("(")[0] for item in res]
        # res = [item.split(":")[1] for item in res]
        res = [item.strip().rstrip("*-").strip() for item in res]
        return res

    def ensure(self, name, cmd, env={}, path="", descr=""):
        """Ensures that the given upstart service is self.running, starting
        it if necessary."""
        self.stop(name=name)

        cmd = self._cuisine.core.args_replace(cmd)
        path = self._cuisine.core.args_replace(path)

        envstr = ""
        for name0, value in list(env.items()):
            envstr += "export %s=%s && " % (name0, value)
        if path:
            cwd = "cd %s &&" % path
            cmd = "%s %s" % (cwd, cmd)
        if envstr != "":
            cmd = "%s%s" % (envstr, cmd)

        self._cuisine.tmux.executeInScreen("main", name, cmd)

    def stop(self, name):
        """Ensures that the given upstart service is stopped."""
        if name in self.list():
            pid = self._cuisine.tmux.getPid('main', name)
            self._cuisine.core.run("kill -9 %s" % pid)
            self._cuisine.tmux.killWindow("main", name)
        self._cuisine.process.kill(name, signal=9, exact=False)

    def remove(self, name):
        """removes service """
        if name in self.list():
            pid = self._cuisine.tmux.getPid('main', name)
            self._cuisine.core.run("kill -9 %s" % pid)
            self._cuisine.tmux.killWindow("main", name)
