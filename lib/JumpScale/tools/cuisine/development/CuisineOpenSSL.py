from JumpScale import j

base = j.tools.cuisine._getBaseClass()

# DANGEROUS
# HIDE OPENSSL
"""
sudo mv -f /usr/local/etc/openssl /usr/local/etc/openssl_
sudo mv -f /usr/local/Cellar/openssl /usr/local/Cellar/openssl_
sudo mv -f /usr/local/include/node/openssl /usr/local/include/node/openssl_
sudo mv -f /usr/local/include/openssl /usr/local/include/openssl_
sudo mv -f /usr/local/opt/openssl /usr/local/opt/openssl_
sudo mv -f /usr/local/ssl /usr/local/ssl_
sudo mv -f /usr/local/bin/openssl /usr/local/bin/openssl_
sudo mv -f /usr/bin/openssl /usr/bin/openssl_
"""

# UNHIDE OPENSSL
"""
sudo mv -f /usr/local/etc/openssl_ /usr/local/etc/openssl
sudo mv -f /usr/local/Cellar/openssl_ /usr/local/Cellar/openssl
sudo mv -f /usr/local/include/node/openssl_ /usr/local/include/node/openssl
sudo mv -f /usr/local/include/openssl_ /usr/local/include/openssl
sudo mv -f /usr/local/opt/openssl_ /usr/local/opt/openssl
sudo mv -f /usr/local/ssl_ /usr/local/ssl
sudo mv -f /usr/local/bin/openssl_ /usr/local/bin/openssl
sudo mv -f /usr/bin/openssl_ /usr/bin/openssl
"""


class CuisineOpenSSL(base):

    def _init(self):
        self.BUILDDIR = self.replace("$BUILDDIR/openssl/")
        self.CODEDIR = self.replace("$CODEDIR/github/openssl/openssl/")

    def build(self, destpath="", reset=False):
        """
        @param destpath, if '' then will be $TMPDIR/build/openssl
        """
        if self.doneGet("build") and not reset:
            return
        if reset:
            self.cuisine.core.run("rm -rf %s" % self.BUILDDIR)

        url = "https://github.com/openssl/openssl.git"
        cpath = self.cuisine.development.git.pullRepo(url, branch="OpenSSL_1_1_0-stable", reset=reset)

        assert cpath.rstrip("/") == self.CODEDIR.rstrip("/")

        if not self.doneGet("compile") or reset:
            C = """
            set -ex
            cd $CODEDIR
            # ./config
            ./Configure darwin64-x86_64-cc shared enable-ec_nistp_64_gcc_128 no-ssl2 no-ssl3 no-comp --openssldir=$BUILDDIR --prefix=$BUILDDIR
            make depend
            make install
            rm -rf $BUILDDIR/share
            rm -rf $BUILDDIR/private
            """
            self.cuisine.core.run(self.replace(C))
            self.doneSet("compile")
            self.log("BUILD DONE")
        else:
            self.log("NO NEED TO BUILD")

        self.log("BUILD COMPLETED OK")
        self.doneSet("build")
