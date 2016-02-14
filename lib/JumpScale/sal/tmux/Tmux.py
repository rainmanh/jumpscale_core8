from JumpScale import j
import time
import os

from sal.base.SALObject import SALObject

class Tmux(SALObject):

    def __init__(self):
        self.__jslocation__ = "j.sal.tmux"
        self.screencmd = "tmux"
        self.executor = j.tools.executor.getLocal()

    def get(self,cuisine,executor):
        o=Tmux()
        o.executor=executor
        o.cuisine=cuisine
        return o

    def createSession(self, sessionname, screens, user=None):
        """
        @param name is name of session
        @screens is list with nr of screens required in session and their names (is [$screenname,...])
        """
        if 'ubuntu' in j.core.platformtype.myplatform.platformtypes:
            j.sal.ubuntu.apt_install_check("tmux", "tmux")
        else:
            if not j.do.checkInstalled("tmux"):
                raise RuntimeError("Cannnot use tmux, please install tmux")

        self.killSession(sessionname)
        if len(screens) < 1:
            raise RuntimeError(
                "Cannot create screens, need at least 1 screen specified")

        env = os.environ.copy()
        env.pop('TMUX', None)
        cmd = "%s new-session -d -s %s -n %s" % (
            self.screencmd, sessionname, screens[0])
        if user is not None:
            cmd = "sudo -u %s -i %s" % (user, cmd)
        # j.sal.process.run(cmd, env=env)  #@todo does not work in python3
        self.executor.execute(cmd,showout=False)
        # now add the other screens to it
        if len(screens) > 1:
            for screen in screens[1:]:
                cmd = "tmux new-window -t '%s' -n '%s'" % (sessionname, screen)
                if user is not None:
                    cmd = "sudo -u %s -i %s" % (user, cmd)
                self.executor.execute(cmd,showout=False)

    def executeInScreen(self, sessionname, screenname, cmd, wait=0, cwd=None, env=None, user="root", tmuxuser=None,reset=True):
        """
        @param sessionname Name of the tmux session
        @type sessionname str
        @param screenname Name of the window in the session
        @type screenname str
        @param cmd command to execute
        @type cmd str
        @param wait time to wait for output
        @type wait int
        @param cwd workingdir for command only in new screen see newscr
        @type cwd str
        @param env environment variables for cmd onlt in new screen see newscr
        @type env dict
        """
        env = env or dict()
        envstr = ""
        for name, value in list(env.items()):
            envstr += "export %s=%s\n" % (name, value)

        # Escape the double quote character in cmd
        cmd = cmd.replace('"', r'\"')

        if reset:
             self.killWindow( sessionname, screenname)

        if cmd.strip():
            self.createWindow(sessionname, screenname, cmd=cmd, user=tmuxuser)
            pane = self._getPane(sessionname, screenname, user=tmuxuser)
            env = os.environ.copy()
            env.pop('TMUX', None)

            if envstr != "":
                cmd2 = "tmux send-keys -t '%s' '%s\n'" % (pane, envstr)
                if tmuxuser is not None:
                    cmd2 = "sudo -u %s -i %s" % (tmuxuser, cmd2)
                self.executor.execute(cmd2, showout=False)

            if cwd:
                cwd = "cd %s;" % cwd
                cmd = "%s %s" % (cwd, cmd)
            if user != "root":
                sudocmd = "su -c \"%s\" %s" % (cmd, user)
                cmd2 = "tmux send-keys -t '%s' '%s' ENTER" % (pane, sudocmd)
            else:
                # if cmd.find("'") != -1:
                #     cmd=cmd.replace("'","\\\'")
                if cmd.find("$") != -1:
                    cmd = cmd.replace("$", "\\$")
                cmd2 = "tmux send-keys -t '%s' \"%s\" ENTER" % (pane, cmd)
            if tmuxuser is not None:
                cmd2 = "sudo -u %s -i %s" % (tmuxuser, cmd2)
            # j.sal.process.run(cmd2, env=env)
            self.executor.execute(cmd2,showout=False)

            time.sleep(wait)

    def getSessions(self, user=None):
        cmd = 'tmux list-sessions -F "#{session_name}"'
        if user:
            cmd = "sudo -u %s -i %s" % (user, cmd)
        exitcode, output = self.executor.execute(cmd, die=False,showout=False)
        if exitcode != 0:
            output = ""
        return [name.strip() for name in output.split()]

    def getPid(self, session, name, user=None):
        cmd = 'tmux list-panes -t "%s" -F "#{pane_pid};#{window_name}" -a' % session
        if user:
            cmd = "sudo -u %s -i %s" % (user, cmd)
        exitcode, output = self.executor.execute(cmd, die=False,showout=False)
        if exitcode > 0:
            return None
        for line in output.split():
            pid, windowname = line.split(';')
            if windowname == name:
                return int(pid)
        return None

    def getWindows(self, session, attemps=5, user=None):
        result = dict()

        cmd = 'tmux list-windows -F "#{window_index}:#{window_name}" -t "%s"' % session
        if user:
            cmd = "sudo -u %s -i %s" % (user, cmd)
        exitcode, output = self.executor.execute(cmd, die=False,showout=False, checkok=False)
        if exitcode != 0:
            return result
        for line in output.split():
            idx, name = line.split(':', 1)
            result[int(idx)] = name
        return result

    def createWindow(self, session, name, user=None, cmd=None):
        if session not in self.getSessions(user=user):
            return self.createSession(session, [name], user=user)
        windows = self.getWindows(session, user=user)
        if name not in list(windows.values()):
            cmd = "tmux new-window -t '%s:' -n '%s'" % (session, name)
            if user:
                cmd = "sudo -u %s -i %s" % (user, cmd)
            self.executor.execute(cmd,showout=False)

    def logWindow(self, session, name, filename, user=None):
        pane = self._getPane(session, name, user=user)
        if pane:
            cmd = "tmux pipe-pane -t '%s' 'cat >> \"%s\"'" % (pane, filename)
            if user:
                cmd = "sudo -u %s -i %s" % (user, cmd)
            self.executor.execute(cmd,showout=False)

    def windowExists(self, session, name, user=None):
        if session in self.getSessions(user=user):
            if name in list(self.getWindows(session, user=user).values()):
                return True
        return False

    def _getPane(self, session, name, user=None):
        windows = self.getWindows(session, user=user)
        remap = dict([(win, idx) for idx, win in list(windows.items())])
        if name not in remap:
            return None
        result = "%s:%s" % (session, remap[name])
        return result

    def killWindow(self, session, name, user=None):
        try:
            pane = self._getPane(session, name, user=user)
        except KeyError:
            return  # window does nt exist
        cmd = "tmux kill-window -t '%s'" % pane
        if user:
            cmd = "sudo -u %s -i %s" % (user, cmd)
        self.executor.execute(cmd, die=False,showout=False)

    def killSessions(self, user=None):
        cmd = "tmux kill-server"
        if user:
            cmd = "sudo -u %s -i %s" % (user, cmd)
        self.executor.execute(cmd, die=False,showout=False)  # todo checking

    def killSession(self, sessionname, user=None):
        cmd = "tmux kill-session -t '%s'" % sessionname
        if user:
            cmd = "sudo -u %s -i %s" % (user, cmd)
        self.executor.execute(cmd, die=False,showout=False)  # todo checking

    def attachSession(self, sessionname, windowname=None, user=None):
        if windowname:
            pane = self._getPane(sessionname, windowname, user=user)
            cmd = "tmux select-window -t '%s'" % pane
            if user:
                cmd = "sudo -u %s -i %s" % (user, cmd)
            self.executor.execute(cmd, die=False)
        cmd = "tmux attach -t %s" % (sessionname)
        if user:
            cmd = "sudo -u %s -i %s" % (user, cmd)
        self.executor.execute(cmd,showout=False)
