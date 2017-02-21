from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineMobidick(app):
    def build(self, build_path="/root/rogerthat/builds"):
        self._cuisine.package.update()
        self._cuisine.package.multiInstall(["git-core"])
        self._cuisine.core.dir_ensure(build_path)
        self._cuisine.core.dir_ensure("/tmp/rogerthat")
        MOBIDICK_URL = "https://github.com/rogerthat-platform/mobidick.git"
        buildscript = """
        set -ex
        REPOS_PATH="/tmp/rogerthat"
        MOBIDICK_REPO=$REPOS_PATH/mobidick
        if [ ! -d "$MOBIDICK_REPO" ]; then
            cd $REPOS_PATH
            git clone {mobidick_url}
        else
            cd $MOBIDICK_REPO
            git pull
        fi
        cd $MOBIDICK_REPO/src && tar -czf {build_path}/mobidick.tar.gz .
        """.format(mobidick_url=MOBIDICK_URL,
                   build_path=build_path)
        self._cuisine.core.run(buildscript, die=True)
        return "%s/mobidick.tar.gz" % build_path
