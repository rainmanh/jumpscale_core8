from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineApache(app):

    NAME = 'httpd'

    def build(self):
        self._cuisine.core.dir_ensure("/opt/owncloudbox")

        C = """
apt-get install wget curl gcc libaprutil1-dev libapr1-dev libpcre3-dev libxml2-dev build-essential unzip -y

rm -rf /opt/owncloudbox/httpd

cd /tmp && wget http://www-eu.apache.org/dist//httpd/httpd-2.4.23.tar.bz2 && tar xvjf /tmp/httpd-2.4.23.tar.bz2

mv /tmp/httpd-2.4.23 /opt/owncloudbox/httpd

#build

cd  /opt/owncloudbox/httpd && ./configure --prefix /opt/owncloudbox/httpd --enable-so && make
        """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.execute_bash(C)

    def install(self, start=False):

        C = """

        cd  /opt/owncloudbox/httpd && make install

        #fix apxs perms
        chmod 764 /opt/owncloudbox/httpd/support/apxs

        #echo to httpdconf mimetypes
        printf "\napplication/x-httpd-php phtml pwml php5 php4 php3 php2 php inc htm html" >> /opt/owncloudbox/httpd/conf/mime.types
        """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.execute_bash(C)

        if start:
            self.start()

    def start(self):
        self._cuisine.core.run("cd /opt/owncloudbox/httpd/bin && ./apachectl start -DFOREGROUND")

    def restart(self):
        self._cuisine.core.run("cd /opt/owncloudbox/httpd/bin && ./apachectl restart")
