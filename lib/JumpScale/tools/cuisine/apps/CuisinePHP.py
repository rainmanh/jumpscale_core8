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

        # build to $tmpDir/php/

        # mysql module
        # postgresql module
        # check modules on:
        # https://www.howtoforge.com/tutorial/installing-nginx-with-php7-fpm-and-mysql-on-ubuntu-16.04-lts-lemp/
        # check if we need an php accelerator: https://en.wikipedia.org/wiki/List_of_PHP_accelerators

    def install(self, start=True):
        C = """
        cd /opt/owncloudbox/php && make install
        #NOT MAKE INSTALL
        """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.execute_bash(C)

        # copy right files of php: $appDir & libraries

    def test(self):
        # TODO: *1
        # check there is a local nginx running, if not install it
        # deploy some php script, test it works
        pass
