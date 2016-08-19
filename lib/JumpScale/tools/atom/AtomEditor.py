from JumpScale import j
import os
try:
    import cson
except:
    rc, out = j.sal.process.execute("pip3 install cson", die=True, outputToStdout=False, ignoreErrorOutput=False)
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
        self.installConfig()

    def installPackagesAll(self):
        self.installPackagesMarkdown()
        self.installPackagesRaml()
        self.installPackagesPython()

    def installPackagesMarkdown(self):
        "Installs packages for markdown"
        items = """
        language-markdown
        markdown-folder
        markdown-mindmap
        markdown-pdf
        markdown-scroll-sync
        markdown-toc
        tidy-markdown
        markdown-preview
        language-gfm
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
        # linter-python-pyflakes
        # linter-pep8
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
        print("install snippets")
        merged = {}
        snippets_existing_path = os.path.expanduser("~/.atom/snippets.cson")
        snippetspath = os.path.join(os.path.dirname(inspect.getfile(self.__class__)), "snippets.cson")
        if j.sal.fs.exists(snippets_existing_path, followlinks=True):
            snippets_existing = j.sal.fs.fileGetContents(snippets_existing_path)
            merged = cson.loads(snippets_existing)
            with open(snippetspath) as jssnippets:
                snippets = cson.load(jssnippets)
                for k, v in snippets.items():
                    if k in merged:
                        merged[k].update(snippets[k])
            content = cson.dumps(merged, indent=4, sort_keys=True)
            j.sal.fs.writeFile(os.path.expanduser("~/.atom/snippets.cson"), content)
        else:
            nc = j.sal.fs.fileGetContents(snippetspath)
            j.sal.fs.writeFile(filename=snippets_existing_path, contents=nc, append=False)

    def installConfig(self):
        print("install atom config")
        merged = {}
        snippets_existing = j.sal.fs.fileGetContents(os.path.expanduser("~/.atom/config.cson"))
        merged = cson.loads(snippets_existing)
        snippets_new_path = os.path.join(os.path.dirname(inspect.getfile(self.__class__)), "config.cson")
        snippets_new = j.sal.fs.fileGetContents(snippets_new_path)
        snippets_new_cson = cson.loads(snippets_new)

        for k0, v0 in snippets_new_cson.items():
            if k0 not in merged:
                merged[k0] = snippets_existing[k0]
            if j.data.types.dict.check(snippets_new_cson[k0]):
                for k1, v1 in snippets_new_cson[k0].items():
                    if k1 not in merged[k0]:
                        merged[k0][k1] = snippets_new_cson[k0][k1]
                    else:
                        merged[k0][k1].update(snippets_new_cson[k0][k1])

        content = cson.dumps(merged, indent=4, sort_keys=True)
        j.sal.fs.writeFile(os.path.expanduser("~/.atom/config.cson"), content)

    def generateJumpscaleAutocompletion(self, dest='/tmp/tempd/jedicomp.txt'):
        raise NotImplemented
        # TODO: *1 completely not clear how this works?
        # TODO: *1 there should be generation from jumpscale to api which can be used inside atom
        apifile = "/tmp/tempd/jumpscale.api"
        jedicomp = "/tmp/tempd/jedi.comp"
        names = ""
        import re
        with open(apifile) as f:

            with open(jedicomp, "w") as jedout:
                for x in re.finditer("(\w.+)\?", f.read()):
                    name = x.group(0).strip("?")
                    jedout.write(name + "= None \n")

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
