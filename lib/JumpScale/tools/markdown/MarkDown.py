
from JumpScale import j


class MarkDown:

    def __init__(self):
        self.__jslocation__ = "j.tools.markdown"

    def installTools(self):
        """
        installs useful tools for markdown
        make sure node & npm has been installed
        """
        j.sal.process.executeWithoutPipe("sudo npm install tidy-markdown -g")

    def tidy(self, path=""):
        """
        walk over files & tidy markdown
        only look for .md files
        if path=="" then start from current path
        """
        if path == "":
            path = j.sal.fs.getcwd()
        for item in j.sal.fs.listFilesInDir(path, True, filter="*.md"):
            cmd = "cat %s|tidy-markdown" % item
            rc, out = j.sal.process.execute(cmd)
            if rc == 0 and len(out.strip()) > 0:
                j.sal.fs.writeFile(filename=item, contents=out, append=False)
