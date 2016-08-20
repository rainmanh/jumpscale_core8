from JumpScale import j


from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.hadoop"

base = j.tools.cuisine.getBaseClass()


class Hadoop(base):

    
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
