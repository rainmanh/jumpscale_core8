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

base=j.tools.cuisine.getBaseClass()
class Hadoop(base):



    @actionrun(action=True)
    def _build(self):
        self.cuisine.installer.base()

        if self.cuisine.core.isUbuntu:
            C= """\
            apt-get install -y apt-get install openjdk-7-jre
            cd $tmpDir
            wget -c http://www-us.apache.org/dist/hadoop/common/hadoop-2.7.2/hadoop-2.7.2.tar.gz
            tar -xf hadoop-2.7.2.tar.gz -C /opt/
            """
            C = self.cuisine.bash.replaceEnvironInText(C)
            C = self.cuisine.core.args_replace(C)
            self.cuisine.core.run_script(C, profile=True, action=True)
            self.cuisine.bash.addPath("/opt/hadoop-2.7.2/bin", action=True)
            self.cuisine.bash.addPath("/opt/hadoop-2.7.2/sbin", action=True)
            self.cuisine.bash.environSet("JAVA_HOME", "/usr/lib/jvm/java-7-openjdk-amd64")
            self.cuisine.bash.environSet("HADOOP_PREFIX", "/opt/hadoop-2.7.2/")
        else:
            raise NotImplementedError("unsupported platform")

    @actionrun()
    def build(self):
        self._build()