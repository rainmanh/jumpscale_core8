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
        Lists all atom packages installed on your system.
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
        self.installPythonExtensions()
        self.installPackagesAll()
        self.installSnippets()

    def installPackagesAll(self):
        self.installPackagesMarkdown()
        self.installPackagesRaml()
        self.installPackagesPython()

    def installPackagesMarkdown(self):
        "Installs packages for markdown"
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

    def installPackagesPython(self):
        "Installs main python packages."
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

    def installPackagesRaml(self):
        "Installs RAML api-workbench package."
        items = """
        api-workbench
        """
        for item in items.split("\n"):
            self.installPackage(item)

    def installSnippets(self):
        """Adds Jumpscale snippets to your atom snippets file."""

        # Note : to add more snippets you they need to be on the same 'key'
        # so we will do a snippets merge based on keys.
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
