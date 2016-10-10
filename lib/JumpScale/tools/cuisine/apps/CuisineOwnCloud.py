from JumpScale import j
import textwrap
app = j.tools.cuisine._getBaseAppClass()


class CuisineOwnCloud(app):

    NAME = 'owncloud'

    def install(self, start=True, storagepath="/var/www/html", sitename="owncloudy.com"):
        """
        install owncloud 9.1 on top of nginx/php/tidb
        tidb is the mysql alternative which is ultra reliable & distributed

        REQUIREMENT: nginx/php/tidb installed before
        """

        C = """
        set -xe
        cd $tmpDir && git clone https://github.com/gig-projects/proj_gig_box.git
        cd $tmpDir && wget https://download.owncloud.org/community/owncloud-9.1.1.tar.bz2 && tar jxf owncloud-9.1.1.tar.bz2
        cd $tmpDir && tar jxf owncloud-9.1.1.tar.bz2

        """
        self._cuisine.core.execute_bash(C)

        # deploy in $appDir/owncloud
        # use nginx/php other cuisine packages

        owncloudsiterules = self._get_default_conf()
        owncloudsiterules = owncloudsiterules.replace("{sitename}", sitename)

        C = """
        # copy owncloud under {storagepath}
        mv $tmpDir/owncloud {storagepath}/


        # copy config.php to new owncloud home httpd/docs
        /bin/cp -Rf $tmpDir/proj_gig_box/ownclouddeployment/owncloud/config.php {storagepath}/owncloud/config/
        # copy gig theme
        /bin/cp -Rf $tmpDir/proj_gig_box/ownclouddeployment/owncloud/gig {storagepath}/owncloud/themes/
        chown -R www-data:www-data {storagepath}/owncloud/
        chmod 777 -R /var/www/html/owncloud/config

        """.format(storagepath=storagepath)
        self._cuisine.core.execute_bash(C)
        self._cuisine.core.file_write("$cfgDir/nginx/etc/sites-enabled/{sitename}".format(sitename=sitename), content=owncloudsiterules)

        # look at which owncloud plugins to enable(pdf, ...)

        # TODO: *1 storage path

    def _get_default_conf(self):
        conf = """\
upstream php-handler {
    server 127.0.0.1:9000;
    #server unix:/var/run/php5-fpm.sock;
}

server {
    listen 80;
    #listen [::]:80 default_server;
	server_name {sitename} ;


    root /var/www/html/owncloud/;

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
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $request_filename;
        fastcgi_param PATH_INFO $fastcgi_path_info;
        # fastcgi_param HTTPS on;
        fastcgi_param modHeadersAvailable true; #Avoid sending the security headers twice
        fastcgi_param front_controller_active true;
        fastcgi_pass php-handler;
        fastcgi_intercept_errors on;
        fastcgi_request_buffering off;
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

   # location ~ ^/([^.]|\.[^p]|\.p[^h]|\.ph[^p]|\.$|\.p$|\.ph$)*$ {
   #     rewrite ^ /index.php$uri;
   # }

}
    """
        conf = textwrap.dedent(conf)
        return conf

    def restart(self):
        pass

    def test(self):
        # TODO: *2
        # call the api up/download a file
        pass

    # def makeSandbox(self, upload=False):
    #     # j.tools.sandboxer.sandboxLibs(path="/opt/owncloudbox", recursive=True)
    #     # j.tools.sandboxer.dedupe("/opt/owncloudbox", "/tmp/storout", name="owncloudspace")
    #     # flistfile = "/tmp/storout/md/owncloudspace.flist"
    #     # j.tools.cuisine.local.apps.stor.upload(flistfile, host=None, source="/opt/owncloudbox")
    #     #
    #
    #     j.tools.sandboxer.sandboxLibs(path="/opt/owncloudbox", recursive=True)
    #     sp = j.tools.cuisine.local.stor.getStorageSpace("owncloudspace")
    #     flistfile = sp.flist("/opt/owncloudbox")
    #     if upload:
    #         sp.upload(flistfile)
