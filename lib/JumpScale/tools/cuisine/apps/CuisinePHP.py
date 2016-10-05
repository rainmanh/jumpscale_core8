from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisinePHP(app):

    NAME = 'php'

    def build(self, **config):
        # **config should include every option as option=value
        # prefix=$appDir/php
        # exec_prefix=$appDir/php
        # https://www.howtoforge.com/tutorial/installing-nginx-with-php7-fpm-and-mysql-on-ubuntu-16.04-lts-lemp/

        ## WIP:

        #TODO: make sure to install multibyte, zip modules
        # needed modules
        defaultconfig = {}
        defaultconfig['enable-zend-multibyte'] = True
        defaultconfig['with-gd'] = True
        defaultconfig['with-jpeg'] = True
        defaultconfig['with-curl'] = True  # apt-get install libcurl4-openssl-dev

        defaultconfig['with-zlib'] = True
        defaultconfig['with-libzip'] = True
        defaultconfig['enable-fpm'] = True
        defaultconfig['enable-opcache'] = True
        defaultconfig['prefix'] = "$appDir/php"
        defaultconfig['exec-prefix'] = "$appDir/php"

        config.update(defaultconfig)

        args_string = ""
        for k, v in config.items():
            k = k.replace("_", "-")
            if v is True:
                args_string += " --{k}".format(k=k)
            else:
                args_string += " --{k}={v}".format(k=k, v=v)

        #print("args string: ", args_string)
        C = """
        cd $tmpDir && wget http://be2.php.net/distributions/php-7.0.11.tar.bz2 && tar xvjf $tmpDir/php-7.0.11.tar.bz2
        #cd $tmpDir && tar xvjf $tmpDir/php-7.0.11.tar.bz2
        mv $tmpDir/php-7.0.11 $tmpDir/php

        #build
        cd $tmpDir/php && ./configure {args_string} && make

        """.format(args_string=args_string)

        self._cuisine.core.dir_ensure("$appDir/php")
        C = self._cuisine.core.args_replace(C)
        #print(C)
        self._cuisine.core.execute_bash(C)


        # build to $tmpDir/php/

        # mysql module
        # postgresql module
        # check modules on:
        #
        # check if we need an php accelerator: https://en.wikipedia.org/wiki/List_of_PHP_accelerators

    def install(self, start=True):
        fpmdefaultconf = """
include=$appDir/php/etc/php-fpm.d/*.conf
        """
        fpmwwwconf = """
;nobody Start a new pool named 'www'.
[www]

;prefix = /path/to/pools/$pool

user =  www-data
group = www-data

listen = 127.0.0.1:9000

listen.allowed_clients = 127.0.0.1

pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
        """
        # make sure to save that configuration file ending with .conf under php/etc/php-fpm.d/www.conf
        C = """
        cd $tmpDir/php && make install
        #NOT MAKE INSTALL
        """


        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.execute_bash(C)
        fpmdefaultconf = self._cuisine.core.args_replace(fpmdefaultconf)
        fpmwwwconf = self._cuisine.core.args_replace(fpmwwwconf)
        self._cuisine.core.file_write("$appDir/php/etc/php-fpm.conf.default", content=fpmdefaultconf)
        self._cuisine.core.file_write("$appDir/php/etc/php-fpm.d/www.conf", content=fpmwwwconf)
        # copy right files of php: $appDir & libraries

    def start(self):
        phpfpmbinpath = '$appDir/php/sbin'

        phpfpmcmd = "$appDir/php/sbin/php-fpm -F -y $appDir/php/etc/php-fpm.conf.default"  # foreground
        phpfpmcmd = self._cuisine.core.args_replace(phpfpmcmd)
        print("CMD: ", phpfpmcmd)
        self._cuisine.processmanager.ensure(name="php-fpm", cmd=phpfpmcmd, path=phpfpmbinpath)

    def test(self):
        # TODO: *1
        # check there is a local nginx running, if not install it
        # deploy some php script, test it works
        raise NotImplementedError
