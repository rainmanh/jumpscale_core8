from JumpScale import j
import textwrap
app = j.tools.cuisine._getBaseAppClass()


class CuisineOwnCloud(app):

    NAME = 'owncloud'

    def install(self, start=True, storagepath="/data/", sitename="owncloudy.com"):
        """
        install owncloud 9.1 on top of nginx/php/tidb
        tidb is the mysql alternative which is ultra reliable & distributed

        REQUIREMENT: nginx/php/tidb installed before
        """
        self._cuisine.package.mdupdate()
        self._cuisine.package.install('bzip2')
        C = """
        set -xe
        cd $tmpDir && [ ! -d $tmpDir/ays_owncloud ] && git clone https://github.com/0-complexity/ays_owncloud
        cd $tmpDir && [ ! -f $tmpDir/owncloud-9.1.1.tar.bz2 ] && wget https://download.owncloud.org/community/owncloud-9.1.1.tar.bz2 && cd $tmpDir && tar jxf owncloud-9.1.1.tar.bz2 && rm owncloud-9.1.1.tar.bz2
        [ ! -d {storagepath} ] && mkdir -p {storagepath}
        """.format(storagepath=storagepath)

        self._cuisine.core.execute_bash(C)

        # deploy in $appDir/owncloud
        # use nginx/php other cuisine packages

        C = """
        set -xe
        rm -rf $appDir/owncloud
        mv $tmpDir/owncloud $appDir/owncloud

        # copy config.php to new owncloud home httpd/docs
        /bin/cp -Rf $tmpDir/ays_owncloud/owncloud/config.php $appDir/owncloud/config/
        # copy gig theme
        /bin/cp -Rf $tmpDir/ays_owncloud/owncloud/gig $appDir/owncloud/themes/


        """

        self._cuisine.core.execute_bash(C)
        gigconf = self._get_default_conf_owncloud()
        gigconf = gigconf % {'storagepath': storagepath}
        self._cuisine.core.file_write("$appDir/owncloud/config/config.php", content=gigconf)

        if start:
            self.start(sitename)
        # look at which owncloud plugins to enable(pdf, ...)
        # TODO: *1 storage path

    def _get_default_conf_owncloud(self):
        return """\
        <?php
        $CONFIG = array (
            'theme' => 'gig',
            'datadirectory' => '%(storagepath)s'
        );
        """

        # <?php
        # $CONFIG = array (
        #   'theme' => 'gig',
        #   'datadirectory' => '/data/',
        #   'instanceid' => 'oc9c63xcgy7l',
        #   'passwordsalt' => 'MB/U0WgxwRZ6BLnzN0reuQ3uwmDUiG',
        #   'secret' => 'pTG61+fi55qjzoCtik7ROHBN8HoH2vrn1SKSIFXBDlZ+g2Sa',
        #   'trusted_domains' =>
        #   array (
        #     0 => 'owncloudy.com',
        #   ),
        #   'overwrite.cli.url' => 'http://owncloudy.com',
        #   'dbtype' => 'mysql',
        #   'version' => '9.1.1.3',
        #   'dbname' => 'owncloud',
        #   'dbhost' => '127.0.0.1',
        #   'dbtableprefix' => 'oc_',
        #   'dbuser' => 'oc_admin',
        #   'dbpassword' => 'l1R5ILt15MOwq/a2KkIMSfW+1GmMEA',
        #   'logtimezone' => 'UTC',
        #   'installed' => true,
        # );

    def _get_default_conf_nginx_site(self):
        conf = """\
        upstream php-handler {
            server 127.0.0.1:9000;
            #server unix:/var/run/php5-fpm.sock;
        }

        server {
            listen 80;
            #listen [::]:80 default_server;
            server_name %(sitename)s;


            root $appDir/owncloud/;

            # Add headers to serve security related headers
            # Before enabling Strict-Transport-Security headers please read into this topic first.
            #add_header Strict-Transport-Security "max-age=15552000; includeSubDomains";

            add_header X-Content-Type-Options nosniff;
            add_header X-Frame-Options "SAMEORIGIN";
            add_header X-XSS-Protection "1; mode=block";
            add_header X-Robots-Tag none;
            add_header X-Download-Options noopen;
            add_header X-Permitted-Cross-Domain-Policies none;

            location = /robots.txt {
                allow all;
                log_not_found off;
                access_log off;
            }

            # The following 2 rules are only needed for the user_webfinger app.
            # Uncomment it if you're planning to use this app.
            #rewrite ^/.well-known/host-meta /public.php?service=host-meta last;
            #rewrite ^/.well-known/host-meta.json /public.php?service=host-meta-json last;

            location = /.well-known/carddav {
                return 301 $scheme://$host/remote.php/dav;
            }
            location = /.well-known/caldav {
                return 301 $scheme://$host/remote.php/dav;
            }

            location /.well-known/acme-challenge { }

            # set max upload size
            client_max_body_size 512M;
            fastcgi_buffers 64 4K;

            # Disable gzip to avoid the removal of the ETag header
            gzip off;

            # Uncomment if your server is build with the ngx_pagespeed module
            # This module is currently not supported.
            #pagespeed off;

            error_page 403 /core/templates/403.php;
            error_page 404 /core/templates/404.php;

            location / {
                rewrite ^ /index.php$uri;
            }

            location ~ ^/(?:build|tests|config|lib|3rdparty|templates|data)/ {
                return 404;
            }
            location ~ ^/(?:\.|autotest|occ|issue|indie|db_|console) {
                return 404;
            }

            location ~ ^/(?:index|remote|public|cron|core/ajax/update|status|ocs/v[12]|updater/.+|ocs-provider/.+|core/templates/40[34])\.php(?:$|/) {
                fastcgi_split_path_info ^(.+\.php)(/.*)$;
                include $appDir/nginx/etc/fastcgi_params;
                fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
                fastcgi_param PATH_INFO $fastcgi_path_info;
                # fastcgi_param HTTPS on;
                fastcgi_param modHeadersAvailable true; #Avoid sending the security headers twice
                fastcgi_param front_controller_active true;
                fastcgi_pass php-handler;
                fastcgi_intercept_errors on;
                fastcgi_request_buffering off;
                fastcgi_read_timeout 300;
            }

            location ~ ^/(?:updater|ocs-provider)(?:$|/) {
                try_files $uri $uri/ =404;
                index index.php;
            }

            # Adding the cache control header for js and css files
            # Make sure it is BELOW the PHP block
            location ~* \.(?:css|js)$ {
                try_files $uri /index.php$uri$is_args$args;
                add_header Cache-Control "public, max-age=7200";
                # Add headers to serve security related headers (It is intended to have those duplicated to the ones above)
                # Before enabling Strict-Transport-Security headers please read into this topic first.
                #add_header Strict-Transport-Security "max-age=15552000; includeSubDomains";
                add_header X-Content-Type-Options nosniff;
                add_header X-Frame-Options "SAMEORIGIN";
                add_header X-XSS-Protection "1; mode=block";
                add_header X-Robots-Tag none;
                add_header X-Download-Options noopen;
                add_header X-Permitted-Cross-Domain-Policies none;
                # Optional: Don't log access to assets
                access_log off;
            }

            location ~* \.(?:svg|gif|png|html|ttf|woff|ico|jpg|jpeg)$ {
                try_files $uri /index.php$uri$is_args$args;
                # Optional: Don't log access to other assets
                access_log off;
            }
        }
        """
        conf = textwrap.dedent(conf)
        conf = self._cuisine.core.args_replace(conf)
        return conf

    def start(self, sitename='owncloudy.com', dbhost="127.0.0.1", dbuser="root", dbpass=""):

        owncloudsiterules = self._get_default_conf_nginx_site()
        owncloudsiterules = owncloudsiterules % {"sitename": sitename}
        self._cuisine.core.file_write("$cfgDir/nginx/etc/sites-enabled/{sitename}".format(sitename=sitename), content=owncloudsiterules)

        privateIp = self._cuisine.net.getInfo(self._cuisine.net.nics[0])['ip'][0]

        C = r"""\
        mysql -h {dbhost} -u {dbuser} -p "{dbpass}" --port 3306 --execute "CREATE DATABASE owncloud"
        mysql -h {dbhost} -u {dbuser} -p "{dbpass}" --port 3306 --execute "CREATE USER 'owncloud'@'{ip}' IDENTIFIED BY 'owncloud'"
        mysql -h {dbhost} -u {dbuser} -p "{dbpass}" --port 3306 --execute "grant all on *.* to 'owncloud'@'{ip}'"
        """.format(dbhost=dbhost, dbuser=dbuser, dbpass=dbpass, ip=privateIp)

        self._cuisine.core.execute_bash(C)

        #TODO: if not installed
        cmd = """
        $appDir/php/bin/php $appDir/owncloud/occ maintenance:install  --database="mysql" --database-name="owncloud"\
        --database-host="{dbhost}" --database-user="owncloud" --database-pass="owncloud" --admin-user="admin" --admin-pass="admin"\
        --data-dir="/data"

        $appDir/php/bin/php $appDir/owncloud/occ config:system:set trusted_domains 1 --value={sitename}
        """.format(dbhost=dbhost, sitename=sitename)

        self._cuisine.core.execute_bash(cmd)

        basicnginxconf = self._cuisine.apps.nginx.get_basic_nginx_conf()
        basicnginxconf = basicnginxconf.replace("include $appDir/nginx/etc/sites-enabled/*;", "include $cfgDir/nginx/etc/sites-enabled/*;")
        basicnginxconf = self._cuisine.core.args_replace(basicnginxconf)
        C = """
        chown -R www-data:www-data $appDir/owncloud $cfgDir/nginx
        chmod 777 -R $appDir/owncloud/config
        chown -R www-data:www-data /data
        """
        self._cuisine.core.execute_bash(C)
        self._cuisine.core.file_write("$cfgDir/nginx/etc/nginx.conf", content=basicnginxconf)
        self._cuisine.processmanager.stop("nginx")
        self._cuisine.apps.nginx.start()
        self._cuisine.development.php.start()

    def restart(self):
        pass

    def test(self):
        # TODO: *2
        # call the api up/download a file
        pass
