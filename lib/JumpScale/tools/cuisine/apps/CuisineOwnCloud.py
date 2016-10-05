from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineOwnCloud(app):

    NAME = 'owncloud'

    def install(self, start=True, storagepath=""):
        """
        install owncloud 9.1 on top of nginx/php/tidb
        tidb is the mysql alternative which is ultra reliable & distributed

        REQUIREMENT: nginx/php/tidb installed before
        """

        C = """

        rm -rf /opt/owncloudbox/httpd/htdocs/owncloud

        cd /tmp && git clone https://github.com/gig-projects/proj_gig_box.git


        #TODO: *1 wrong version
        cd /tmp && wget https://download.owncloud.org/community/owncloud-9.0.0.zip && unzip -a /tmp/owncloud-9.0.0.zip

        """
        C = self._cuisine.core.args_replace(C)  # option in execute, no need to do this
        self._cuisine.core.execute_bash(C)

        # deploy in $appDir/owncloud
        # use nginx/php other cuisine packages

        C = """
        # copy owncloud under httpd/htdocs
        /bin/cp -Rf /tmp/owncloud/ /opt/owncloudbox/httpd/htdocs/

        /bin/cp -Rf /tmp/proj_gig_box/ownclouddeployment/owncloud/gig /opt/owncloudbox/httpd/htdocs/ownlcloud/


        # copy config.php to new owncloud home httpd/docs
        /bin/cp -Rf /opt/owncloudbox/proj_gig_box/ownclouddeployment/owncloud/config.php /opt/owncloudbox/httpd/htdocs/owncloud/config/
        # copy gig theme
        /bin/cp -Rf /opt/owncloudbox/proj_gig_box/ownclouddeployment/owncloud/gig /opt/owncloudbox/httpd/htdocs/owncloud/themes/
        chown -R www-data:www-data /opt/owncloudbox/owncloud/
        chmod 770 -R /opt/owncloudbox/owncloud

        """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.execute_bash(C)

        # look at which owncloud plugins to enable(pdf, ...)

        # TODO: *1 storage path

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
