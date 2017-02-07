from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineAppscale(app):
    def build(self, tag=""):
        BOOTSTRAP_URL = "https://raw.githubusercontent.com/AppScale/appscale/master/bootstrap.sh"
        buildscript = """
        set -ex
        export HOME="/root"
        cd $HOME
        curl -k {BOOTSTRAP_URL} > bootstrap.sh
        bash bootstrap.sh --tag {tag}
        """.format(BOOTSTRAP_URL=BOOTSTRAP_URL, tag=tag)

        self._cuisine.core.run(buildscript)

        # Appscale dashoard deps
        j.tools.cuisine.local.development.pip.multiInstall([
            "webapp2",
            "webob",
            "jinja2",
        ])

    def build_tools(self):
        APPSCALE_TOOLS_URL = "https://github.com/AppScale/appscale-tools.git"
        buildscript = """
        set -ex
        export HOME="/root"
        cd $HOME
        git clone {APPSCALE_TOOLS_URL}
        ./appscale-tools/debian/appscale_build.sh
        """.format(APPSCALE_TOOLS_URL=APPSCALE_TOOLS_URL)

        self._cuisine.core.run(buildscript)
