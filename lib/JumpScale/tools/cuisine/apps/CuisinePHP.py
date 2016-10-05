from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisinePHP(app):

    NAME = 'php'

    def build(self):
        C = """
rm -rf /opt/owncloudbox/php
cd /opt/owncloudbox && wget http://be2.php.net/distributions/php-7.0.11.tar.bz2 && tar xvjf /opt/owncloudbox/php-7.0.11.tar.bz2

mv /opt/owncloudbox/php-7.0.11 /opt/owncloudbox/php

#build
cd /opt/owncloudbox/php && ./configure --with-apxs2=/opt/owncloudbox/httpd/support/apxs --prefix=/opt/owncloudbox/php/ --exec-prefix=/opt/owncloudbox/php/ --with-config-file-scan-dir=/opt/owncloudbox/php/lib && make

#echo to httpdconf mimetypes
echo "\napplication/x-httpd-php phtml pwml php5 php4 php3 php2 php inc htm html" >> /opt/owncloudbox/httpd/conf/mime.types


        """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.execute_bash(C)

    def install(self, start=True):
        C = """
    cd /opt/owncloudbox/php && make install

        """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.execute_bash(C)

    def start(self):
        pass

    def restart(self):
        pass
