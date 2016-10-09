from JumpScale import j
import textwrap
from time import sleep


app = j.tools.cuisine._getBaseAppClass()


class CuisineNGINX(app):
    NAME = 'nginx'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def _build(self):
        # TODO: *3 optional
        # build nginx
        return True

    def install(self, start=True):
        """
        can install through ubuntu

        """
        # Install through ubuntu
        self._cuisine.package.ensure('nginx')
        # link nginx to binDir and use it from there

        self._cuisine.core.dir_ensure("$appDir/nginx/")
        self._cuisine.core.dir_ensure("$appDir/nginx/bin")
        self._cuisine.core.dir_ensure("$appDir/nginx/etc")

        self._cuisine.core.file_link(source='/usr/sbin/nginx', destination='$appDir/nginx/bin/nginx')
        self._cuisine.core.dir_ensure('/var/log/nginx')
        self._cuisine.core.file_copy('/etc/nginx/*', '$appDir/nginx/etc/', recursive=True)

        basicnginxconf = """\
        user www-data;
        worker_processes auto;
        pid /run/nginx.pid;

        events {
        	worker_connections 768;
        	# multi_accept on;
        }

        http {

        	##
        	# Basic Settings
        	##

        	sendfile on;
        	tcp_nopush on;
        	tcp_nodelay on;
        	keepalive_timeout 65;
        	types_hash_max_size 2048;
        	# server_tokens off;

        	# server_names_hash_bucket_size 64;
        	# server_name_in_redirect off;

        	include /etc/nginx/mime.types;
        	default_type application/octet-stream;

        	##
        	# SSL Settings
        	##

        	ssl_protocols TLSv1 TLSv1.1 TLSv1.2; # Dropping SSLv3, ref: POODLE
        	ssl_prefer_server_ciphers on;

        	##
        	# Logging Settings
        	##

        	access_log /var/log/nginx/access.log;
        	error_log /var/log/nginx/error.log;

        	##
        	# Gzip Settings
        	##

        	gzip on;
        	gzip_disable "msie6";

        	# gzip_vary on;
        	# gzip_proxied any;
        	# gzip_comp_level 6;
        	# gzip_buffers 16 8k;
        	# gzip_http_version 1.1;
        	# gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

        	##
        	# Virtual Host Configs
        	##

        	include /etc/nginx/conf.d/*.conf;
        	include /etc/nginx/sites-enabled/*;
        }


        #mail {
        #	# See sample authentication script at:
        #	# http://wiki.nginx.org/ImapAuthenticateWithApachePhpScript
        #
        #	# auth_http localhost/auth.php;
        #	# pop3_capabilities "TOP" "USER";
        #	# imap_capabilities "IMAP4rev1" "UIDPLUS";
        #
        #	server {
        #		listen     localhost:110;
        #		protocol   pop3;
        #		proxy      on;
        #	}
        #
        #	server {
        #		listen     localhost:143;
        #		protocol   imap;
        #		proxy      on;
        #	}
        #}


        """
        defaultenabledsitesconf = """\

        server {
            listen 80 default_server;
            listen [::]:80 default_server;



            root /var/www/html;

            # Add index.php to the list if you are using PHP
            index index.html index.htm index.nginx-debian.html index.php;

            server_name _;

            location / {
                # First attempt to serve request as file, then
                # as directory, then fall back to displaying a 404.
                try_files $uri $uri/ =404;
            }

            # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000

            location ~ \.php$ {
                include snippets/fastcgi-php.conf;

            #   # With php7.0-cgi alone:
                fastcgi_pass 127.0.0.1:9000;
                # With php7.0-fpm:
                # fastcgi_pass unix:/run/php/php7.0-fpm.sock;
            }

            # deny access to .htaccess files, if Apache's document root
            # concurs with nginx's one
            #
            #location ~ /\.ht {
            #   deny all;
            #}
        }

        """
        basicnginxconf = textwrap.dedent(basicnginxconf)
        defaultenabledsitesconf = textwrap.dedent(defaultenabledsitesconf)

        self._cuisine.core.file_write("$appDir/nginx/etc/nginx.conf", content=basicnginxconf)
        self._cuisine.core.file_write("$appDir/nginx/etc/sites-enabled/default", content=defaultenabledsitesconf)
        if start:
            self.start()

    def build(self, start=True, install=True):
        self._build()
        if install:
            self.install(start)

    def start(self, name="nginx", nodaemon=True, nginxconfpath=None):
        nginxbinpath = '$appDir/nginx'
        if nginxconfpath is None:
            nginxconfpath = '$appDir/nginx/etc/nginx.conf'
        nginxcmd = "$appDir/nginx/bin/nginx -c {nginxconfpath} -g 'daemon off;'".format(nginxconfpath=nginxconfpath)  # foreground
        nginxcmd = self._cuisine.core.args_replace(nginxcmd)
        print("cmd: ", nginxcmd)
        self._cuisine.processmanager.ensure(name=name, cmd=nginxcmd, path=nginxbinpath)

    def test(self):
        # host a file test can be reached
        raise NotImplementedError
