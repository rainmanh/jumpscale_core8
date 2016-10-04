from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineOwnCloud(app):

    NAME = 'owncloud'

    def build(self):

        C = """

rm -rf /opt/owncloudbox/httpd/htdocs/owncloud
cd /opt/owncloudbox && git clone https://github.com/gig-projects/proj_gig_box.git

cd /opt/owncloudbox && wget https://download.owncloud.org/community/owncloud-9.0.0.zip && unzip -a /opt/owncloudbox/owncloud-9.0.0.zip

# copy owncloud under httpd/htdocs
/bin/cp -Rf /opt/owncloudbox/owncloud/ /opt/owncloudbox/httpd/htdocs/

/bin/cp -Rf /opt/owncloudbox/proj_gig_box/ownclouddeployment/owncloud/gig /opt/owncloudbox/httpd/htdocs/ownlcloud/


# copy config.php to new owncloud home httpd/docs
/bin/cp -Rf /opt/owncloudbox/proj_gig_box/ownclouddeployment/owncloud/config.php /opt/owncloudbox/httpd/htdocs/owncloud/config/
# copy gig theme
/bin/cp -Rf /opt/owncloudbox/proj_gig_box/ownclouddeployment/owncloud/gig /opt/owncloudbox/httpd/htdocs/owncloud/themes/
chmod 755 -R /opt/owncloudbox/owncloud/config
        """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.execute_bash(C)

    def makeSandbox(self, upload=False):
        # j.tools.sandboxer.sandboxLibs(path="/opt/owncloudbox", recursive=True)
        # j.tools.sandboxer.dedupe("/opt/owncloudbox", "/tmp/storout", name="owncloudspace")
        # flistfile = "/tmp/storout/md/owncloudspace.flist"
        # j.tools.cuisine.local.apps.stor.upload(flistfile, host=None, source="/opt/owncloudbox")
        #

        j.tools.sandboxer.sandboxLibs(path="/opt/owncloudbox", recursive=True)
        sp = j.tools.cuisine.local.stor.getStorageSpace("owncloudspace")
        flistfile = sp.flist("/opt/owncloudbox")
        if upload:
            sp.upload(flistfile)
