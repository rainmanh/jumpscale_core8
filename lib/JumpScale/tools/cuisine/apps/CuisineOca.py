from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineOca(app):
    def build(self, client_id, client_secret, build_path="/root/rogerthat/builds"):
        self._cuisine.package.update()
        self._cuisine.package.multiInstall(["git-core", "python-pip", "python", "libxml2-dev", "libxslt1-dev"])
        self._cuisine.core.dir_ensure(build_path)
        self._cuisine.core.dir_ensure("/tmp/rogerthat")
        ROGERTHAT_URL = "https://github.com/rogerthat-platform/rogerthat-backend.git"
        OCA_URL = "https://github.com/our-city-app/oca-backend.git"
        buildscript = """
        set -ex
        REPOS_PATH="/tmp/rogerthat"
        ROGERTHAT_REPO=$REPOS_PATH/rogerthat-backend
        OCA_REPO=$REPOS_PATH/oca-backend
        if [ ! -d "$ROGERTHAT_REPO" ]; then
            cd $REPOS_PATH
            git clone {rogerthat_url}
            pip2 install -r $ROGERTHAT_REPO/requirements.txt
        else
            cd $ROGERTHAT_REPO
            git pull
            pip2 install -r $ROGERTHAT_REPO/requirements.txt
        fi
        if [ ! -d "$OCA_REPO" ]; then
            cd $REPOS_PATH
            git clone {oca_url}
        else
            cd $OCA_REPO
            git pull
        fi
        cd $OCA_REPO
        echo -e "SHOP_OAUTH_CLIENT_ID = u'{client_id}'\nSHOP_OAUTH_CLIENT_SECRET = u'{client_secret}'" > $OCA_REPO/src/solution_server_settings/consts.py
        rm -rf $OCA_REPO/build
        python2 $OCA_REPO/build.py
        cd $OCA_REPO/build && tar -czf {build_path}/oca.tar.gz .
        """.format(rogerthat_url=ROGERTHAT_URL,
                   oca_url=OCA_URL,
                   client_id=client_id,
                   client_secret=client_secret,
                   build_path=build_path)
        self._cuisine.core.run(buildscript, die=True)
        return "%s/oca.tar.gz" % build_path
