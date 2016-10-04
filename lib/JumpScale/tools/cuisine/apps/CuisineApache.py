from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineApache(app):

    NAME = 'httpd'

    def build(self, start=True):

        C = """
apt-get install wget curl gcc libaprutil1-dev libapr1-dev libpcre3-dev libxml2-dev build-essential unzip -y

rm -rf /opt/owncloudbox/httpd

mkdir /opt/owncloudbox

cd /opt/owncloudbox && wget http://www-eu.apache.org/dist//httpd/httpd-2.4.23.tar.bz2 && tar xvjf /opt/owncloudbox/httpd-2.4.23.tar.bz2

mv /opt/owncloudbox/httpd-2.4.23 /opt/owncloudbox/httpd

#build

cd  /opt/owncloudbox/httpd && ./configure --prefix /opt/owncloudbox/httpd --enable-so && make && make install
#fix apxs perms

chmod 764 /opt/owncloudbox/httpd/support/apxs
        """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.execute_bash(C)

        if start:
            self.start()

    def start(self):
        self._cuisine.core.run("cd /opt/owncloudbox/httpd/bin && ./apachectl start -DFOREGROUND")

    def restart(self):
        self._cuisine.core.run("cd /opt/owncloudbox/httpd/bin && ./apachectl restart")
