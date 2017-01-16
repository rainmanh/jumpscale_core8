from JumpScale import j
import textwrap

app = j.tools.cuisine._getBaseAppClass()


class CuisineApache(app):

    NAME = 'httpd'

    def build(self):
        self._cuisine.core.dir_ensure("/optvar/build")

        C = """
        apt-get install wget curl gcc libaprutil1-dev libapr1-dev libpcre3-dev libxml2-dev build-essential unzip -y
        rm -rf /optvar/build/httpd
        cd /tmp && wget http://www-eu.apache.org/dist//httpd/httpd-2.4.25.tar.bz2 && tar xvjf /tmp/httpd-2.4.25.tar.bz2
        mv /tmp/httpd-2.4.25 /optvar/build/httpd

        #build

        cd  /optvar/build/httpd && ./configure --prefix /optvar/build/httpd --enable-so && make
        """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.run(C)

    def get_default_apache_conf(self):
        self._cuisine.core.file_download("http://pastebin.com/raw/h2n6EziL", "/optvar/build/httpd/conf/mods.conf")
        modsconf = self._cuisine.core.file_read("/optvar/build/httpd/conf/mods.conf")
        return modsconf + textwrap.dedent("""\

            # Global configuration
            #
            LoadModule unixd_module modules/mod_unixd.so
            #
            # ServerRoot: The top of the directory tree under which the server's
            # configuration, error, and log files are kept.
            #
            # NOTE!  If you intend to place this on an NFS (or otherwise network)
            # mounted filesystem then please read the Mutex documentation (available
            # at <URL:http://httpd.apache.org/docs/2.4/mod/core.html#mutex>);
            # you will save yourself a lot of trouble.
            #
            # Do NOT add a slash at the end of the directory path.
            #
            #ServerRoot "/etc/apache2"

            #
            # The accept serialization lock file MUST BE STORED ON A LOCAL DISK.
            #
            Mutex file:/tmp/ default

            #
            # PidFile: The file in which the server should record its process
            # identification number when it starts.
            # This needs to be set in /etc/apache2/envvars
            #
            PidFile /optvar/tmp/apache.pid

            #
            # Timeout: The number of seconds before receives and sends time out.
            #
            Timeout 300

            #
            # KeepAlive: Whether or not to allow persistent connections (more than
            # one request per connection). Set to "Off" to deactivate.
            #
            KeepAlive On

            #
            # MaxKeepAliveRequests: The maximum number of requests to allow
            # during a persistent connection. Set to 0 to allow an unlimited amount.
            # We recommend you leave this number high, for maximum performance.
            #
            MaxKeepAliveRequests 100

            #
            # KeepAliveTimeout: Number of seconds to wait for the next request from the
            # same client on the same connection.
            #
            KeepAliveTimeout 5


            # These need to be set in /etc/apache2/envvars
            User www-data
            Group www-data

            #
            # HostnameLookups: Log the names of clients or just their IP addresses
            # e.g., www.apache.org (on) or 204.62.129.132 (off).
            # The default is off because it'd be overall better for the net if people
            # had to knowingly turn this feature on, since enabling it means that
            # each client request will result in AT LEAST one lookup request to the
            # nameserver.
            #
            HostnameLookups Off

            # ErrorLog: The location of the error log file.
            # If you do not specify an ErrorLog directive within a <VirtualHost>
            # container, error messages relating to that virtual host will be
            # logged here.  If you *do* define an error logfile for a <VirtualHost>
            # container, that host's errors will be logged there and not here.
            #
            ErrorLog /optvar/log/error.log

            #
            # LogLevel: Control the severity of messages logged to the error_log.
            # Available values: trace8, ..., trace1, debug, info, notice, warn,
            # error, crit, alert, emerg.
            # It is also possible to configure the log level for particular modules, e.g.
            # "LogLevel info ssl:warn"
            #
            LogLevel warn

            # Include module configuration:
            # IncludeOptional mods-enabled/*.load
            # IncludeOptional mods-enabled/*.conf

            # Include list of ports to listen on
            Listen 80

            <IfModule ssl_module>
            	Listen 443
            </IfModule>

            <IfModule mod_gnutls.c>
            	Listen 443
            </IfModule>

            # Sets the default security model of the Apache2 HTTPD server. It does
            # not allow access to the root filesystem outside of /usr/share and /var/www.
            # The former is used by web applications packaged in Debian,
            # the latter may be used for local directories served by the web server. If
            # your system is serving content from a sub-directory in /srv you must allow
            # access here, or in any related virtual host.
            <Directory />
            	Options FollowSymLinks
            	AllowOverride None
            	Require all denied
            </Directory>

            <Directory /usr/share>
            	AllowOverride None
            	Require all granted
            </Directory>

            <Directory /var/www/>
            	Options Indexes FollowSymLinks
            	AllowOverride None
            	Require all granted
            </Directory>

            #<Directory /srv/>
            #	Options Indexes FollowSymLinks
            #	AllowOverride None
            #	Require all granted
            #</Directory>

            # AccessFileName: The name of the file to look for in each directory
            # for additional configuration directives.  See also the AllowOverride
            # directive.
            #
            AccessFileName .htaccess

            #
            # The following lines prevent .htaccess and .htpasswd files from being
            # viewed by Web clients.
            #
            <FilesMatch "^\.ht">
            	Require all denied
            </FilesMatch>
            #
            # The following directives define some format nicknames for use with
            # a CustomLog directive.
            #
            # These deviate from the Common Log Format definitions in that they use %O
            # (the actual bytes sent including headers) instead of %b (the size of the
            # requested file), because the latter makes it impossible to detect partial
            # requests.
            #
            # Note that the use of %{X-Forwarded-For}i instead of %h is not recommended.
            # Use mod_remoteip instead.
            #
            LogFormat "%v:%p %h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"" vhost_combined
            LogFormat "%h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"" combined
            LogFormat "%h %l %u %t \"%r\" %>s %O" common
            LogFormat "%{Referer}i -> %U" referer
            LogFormat "%{User-agent}i" agent


        """)
    def install(self, start=False):

        C = """

        cd  /optvar/build/httpd && make install

        #fix apxs perms
        chmod 764 /optvar/build/httpd/support/apxs

        #echo to httpdconf mimetypes
        printf "\napplication/x-httpd-php phtml pwml php5 php4 php3 php2 php inc htm html" >> /optvar/build/httpd/conf/mime.types

        """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.run(C)

        if start:
            self.start()

    def start(self):
        """start Apache."""
        self._cuisine.core.run("cd /optvar/build/httpd/bin && ./apachectl start")

    def stop(self):
        """stop Apache."""
        self._cuisine.core.run("cd /optvar/build/httpd/bin && ./apachectl stop")

    def restart(self):
        """restart Apache."""
        self._cuisine.core.run("cd /optvar/build/httpd/bin && ./apachectl restart")
