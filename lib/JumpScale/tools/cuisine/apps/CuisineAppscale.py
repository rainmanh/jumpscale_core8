from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineAppscale(app):
    def build(self, tag="last"):
        self._cuisine.package.update()
        BOOTSTRAP_URL = "https://raw.githubusercontent.com/AppScale/appscale/master/bootstrap.sh"
        buildscript = """
        set -ex
        export HOME="/root"
        cd $HOME
        curl -k {BOOTSTRAP_URL} > bootstrap.sh
        bash bootstrap.sh --tag {tag}
        pip2 install webapp2 webob jinja2
        """.format(BOOTSTRAP_URL=BOOTSTRAP_URL, tag=tag)

        self._cuisine.core.run(buildscript)

    def build_tools(self, tag="last"):
        self._cuisine.package.update()
        self._cuisine.package.multiInstall("git-core")
        APPSCALE_TOOLS_URL = "https://github.com/AppScale/appscale-tools.git"
        buildscript = """
        set -ex
        export HOME="/root"
        cd $HOME
        REPO=appscale-tools
        GIT_TAG={tag}
        if [ ! -d "$REPO" ]; then
            git clone {APPSCALE_TOOLS_URL}
        fi
        if [ "$GIT_TAG" != "dev" ]; then
            if [ "$GIT_TAG" = "last" ]; then
                GIT_TAG="$(cd appscale-tools; git tag | tail -n 1)"
            fi
            cd $HOME/appscale-tools
            git fetch && git checkout tags/$GIT_TAG
        fi
        if [ "$GIT_TAG" = "dev" ]; then
            GIT_TAG="$(cd appscale-tools; git tag | tail -n 1)"
            cd $HOME/appscale-tools
            git fetch && git checkout master && git pull
        fi
        ./debian/appscale_build.sh
        """.format(APPSCALE_TOOLS_URL=APPSCALE_TOOLS_URL, tag=tag)

        self._cuisine.core.run(buildscript)
