from JumpScale import j

base = j.tools.cuisine._getBaseClass()

# TODO: *4 unfinished but ok for now


class CuisineHadoop(base):

    def _build(self):
        self._cuisine.installer.base()

        if self._cuisine.core.isUbuntu:
            C = """\
            apt-get install -y apt-get install openjdk-7-jre
            cd $tmpDir
            wget -c http://www-us.apache.org/dist/hadoop/common/hadoop-2.7.2/hadoop-2.7.2.tar.gz
            tar -xf hadoop-2.7.2.tar.gz -C /opt/
            """
            C = self._cuisine.bash.replaceEnvironInText(C)
            C = self._cuisine.core.args_replace(C)
            self._cuisine.core.run_script(C, profile=True)
            self._cuisine.bash.addPath("/opt/hadoop-2.7.2/bin")
            self._cuisine.bash.addPath("/opt/hadoop-2.7.2/sbin")
            self._cuisine.bash.environSet("JAVA_HOME", "/usr/lib/jvm/java-7-openjdk-amd64")
            self._cuisine.bash.environSet("HADOOP_PREFIX", "/opt/hadoop-2.7.2/")
        else:
            raise NotImplementedError("unsupported platform")

    def build(self):
        self._build()
