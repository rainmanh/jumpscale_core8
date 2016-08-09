
from JumpScale import j


class AtomEditor:

    def __init__(self):
        self.__jslocation__ = "j.tools.atom"
        self._packages = []

    @property
    def packages(self):
        """
        """
        if self._packages == []:
            cmd = "apm list -b"
            rc, out = j.sal.process.execute(cmd, die=True, outputToStdout=False, ignoreErrorOutput=False)
            items = [item.split("@")[0] for item in out.split("\n") if item.strip() != ""]
            self._packages = items

        return self._packages

    def installPackage(self, name, upgrade=False):
        if name.strip() is "":
            return
        name = name.strip()
        if name.startswith("#"):
            return
        if upgrade is False and name in self.packages:
            return
        cmd = "apm install %s" % name
        rc, out = j.sal.process.execute(cmd, die=True, outputToStdout=False, ignoreErrorOutput=False)

    def installAll(self):
        # TODO: *1 bug in installPackagesAll see below, 3x same & cache?
        """
        [Tue09 09:42] - ...umpScale/sal/process/SystemProcess.py:1336 - INFO     - exec:apm list -b
        [Tue09 09:42] - ...umpScale/sal/process/SystemProcess.py:1383 - INFO     - system.process.execute [apm list -b]
        [Tue09 09:42] - ...umpScale/sal/process/SystemProcess.py:1336 - INFO     - exec:apm list -b
        [Tue09 09:42] - ...umpScale/sal/process/SystemProcess.py:1383 - INFO     - system.process.execute [apm list -b]
        [Tue09 09:42] - ...umpScale/sal/process/SystemProcess.py:1336 - INFO     - exec:apm list -b
        [Tue09 09:42] - ...umpScale/sal/process/SystemProcess.py:1383 - INFO     - system.process.execute [apm list -b]
        """
        self.installPythonExtensions()
        self.installPackagesAll()
        self.installSnippets()

    def installPackagesAll(self):
        self.installPackagesMarkdown()
        self.installPackagesRaml()
        self.installPackagesPython()

    def installPackagesMarkdown(self):
        items = """
        language-markdown
        markdown-format
        markdown-mindmap
        markdown-pdf
        markdown-scroll-sync
        markdown-toc
        """
        for item in items.split("\n"):
            self.installPackage(item)
        self._packages = []

    def installPackagesPython(self):
        items = """
        language-capnproto
        todo-manager
        git-time-machine
        flatten-json
        bottom-dock
        autocomplete-python
        linter
        linter-flake8
        linter-python-pep8
        #linter-python-pyflakes
        #linter-pep8
        """
        for item in items.split("\n"):
            self.installPackage(item)
        self._packages = []

    def installPackagesRaml(self):
        items = """
        api-workbench
        """
        for item in items.split("\n"):
            self.installPackage(item)
        self._packages = []

    def installSnippets(self):
        # TODO: *1 get snippets.cson & copy to right directory

    def generateJummpscaleAutocompletion(self):
        # TODO: *1 use j.tools.objectinspector.inspect() (FIX) and generate jedi
        # code completion, check in ATOM that it works, needs to be installed
        # automatically
        # TODO: walk over all jumpscale extensions & create autocompletion for atom and copy to appropriate directory

    def installPythonExtensions(self):
        """
        """
        # TODO: *1 implement atom plugin install

        C = """
        pip3 install autopep8
        pip3 install flake8
        pip3 install flake8-docstrings
        """
        rc, out = j.sal.process.execute(C, die=True, outputToStdout=False, ignoreErrorOutput=False)
