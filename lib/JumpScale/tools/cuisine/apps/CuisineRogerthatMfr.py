from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineRogerthatMfr(app):
    def build(self, build_path="/root/rogerthat/builds"):
        self._cuisine.package.update()
        self._cuisine.package.multiInstall(["git-core", "unzip", "ant", "zip"])
        self._cuisine.core.dir_ensure(build_path)
        self._cuisine.core.dir_ensure("/tmp/rogerthat")
        ROGERTHAT_MFR_URL = "https://github.com/rogerthat-platform/rogerthat-mfr.git"
        JAVA_GAE_URL = "http://central.maven.org/maven2/com/google/appengine/appengine-java-sdk/1.8.4/appengine-java-sdk-1.8.4.zip"
        buildscript = """
        set -ex
        # Install java-7-oracle
        add-apt-repository -y ppa:webupd8team/java
        apt-get update
        echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections
        echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections
        apt-get -y install oracle-java7-installer

        REPOS_PATH="/tmp/rogerthat"
        ROGERTHAT_MFR_REPO=$REPOS_PATH/rogerthat-mfr
        GAEDIR="/opt"
        cd $GAEDIR  && wget {java_gae_url} && unzip appengine-java-sdk-1.8.4.zip
        if [ ! -d "$ROGERTHAT_MFR_REPO" ]; then
            cd $REPOS_PATH
            git clone {rogerthat_mfr_url}
        else
            cd $ROGERTHAT_MFR_REPO
            git pull
        fi
        cd $ROGERTHAT_MFR_REPO && JAVA_HOME=/usr/lib/jvm/java-7-oracle ant war -DGAE_SDK=/opt/appengine-java-sdk-1.8.4 -DGAE_VERSION=1.8.4
        mv war.zip {build_path}
        cd {build_path} && unzip war.zip -d war
        cd war && tar -czf {build_path}/mfr.tar.gz .
        """.format(rogerthat_mfr_url=ROGERTHAT_MFR_URL,
                   build_path=build_path,
                   java_gae_url=JAVA_GAE_URL)
        self._cuisine.core.run(buildscript, die=True)
        return "%s/mfr.tar.gz" % build_path
