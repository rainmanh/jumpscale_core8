from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineOwnCloud(app):

    NAME = 'owncloud'

    def install(self, start=True, storagepath="/var/www/html"):
        """
        install owncloud 9.1 on top of nginx/php/tidb
        tidb is the mysql alternative which is ultra reliable & distributed

        REQUIREMENT: nginx/php/tidb installed before
        """

        C = """
        set -xe
        cd $tmpDir && git clone https://github.com/gig-projects/proj_gig_box.git
        #cd $tmpDir && wget https://download.owncloud.org/community/owncloud-9.1.1.tar.bz2 && tar jxf owncloud-9.1.1.tar.bz2
        cd $tmpDir && tar jxf owncloud-9.1.1.tar.bz2

        """
        self._cuisine.core.execute_bash(C)

        # deploy in $appDir/owncloud
        # use nginx/php other cuisine packages

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
