from JumpScale import j
import os
import cson
import inspect

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
        #add to ~/.atom/snippets.cson
        #NOTE: If we just append -> it'll overwrite it. We need to merge on keys not to lose old snippets the user got.
        #So we merge on KEY.
        merged = {}
        atomlocalsnippets = os.path.expanduser("~/.atom/snippets.cson")
        if os.path.exists(atomlocalsnippets):
            with open(atomlocalsnippets) as f:
                merged = cson.load(f)
        snippetspath = os.path.join(os.path.dirname(inspect.getfile(self.__class__)), "snippets.cson")
        if os.path.exists(snippetspath):
            with open(snippetspath)  as jssnippets:
                snippets = cson.load(jssnippets)
                for k,v in snippets.items():
                    if k in merged:
                        merged[k].update(snippets[k])
        with open(os.path.expanduser("~/.atom/snippets.cson", 'w')) as out:
            cson.dump(merged, out)


    def generateJummpscaleAutocompletion(self):
        # TODO: *1 use j.tools.objectinspector.inspect() (FIX) and generate jedi
        # code completion, check in ATOM that it works, needs to be installed
        # automatically
        pass

        # TODO: walk over all jumpscale extensions & create autocompletion for atom and copy to appropriate directory

    def installPythonExtensions(self):
        """
        pip installs flake8, autopep8.
        """

        C = """
        pip3 install autopep8
        pip3 install flake8
        pip3 install flake8-docstrings
        """
        rc, out = j.sal.process.execute(C, die=True, outputToStdout=False, ignoreErrorOutput=False)

