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

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def build(self, destpath="", reset=False):
        """
        @param destpath, if '' then will be $tmpDir/build/openssl
        """

        if destpath == "":
            destpath = "$tmpDir/build/openssl/"
        destpath = self._cuisine.core.args_replace(destpath)

        if reset:
            self._cuisine.core.run("rm -rf %s" % destpath)

        url = "https://github.com/openssl/openssl.git"
        cpath = self._cuisine.development.git.pullRepo(url, branch="OpenSSL_1_1_0-stable", reset=reset)

        C = """
        cd %s
        # ./config
        ./Configure darwin64-x86_64-cc shared enable-ec_nistp_64_gcc_128 no-ssl2 no-ssl3 no-comp --openssldir=%s --prefix=%s
        make depend
        make install
        rm -rf %s/share
        rm -rf %s/private
        """ % (cpath, destpath, destpath, destpath, destpath)

        self._cuisine.core.run(C)
        # print("COMPILE DONE")

        # from IPython import embed
        # print("DEBUG NOW ooo")
        # embed()
        # raise RuntimeError("stop debug here")
        #
        # C = """
        # set -ex
        # cd %s
        # mkdir -p $dest
        # # set +ex  #TODO: *1 should not give error. but works
        # find . -name "*.dylib" -exec cp {} $dest/ \;
        # find . -name "*.a" -exec cp {} $dest/ \;
        # find . -name "*.so" -exec cp {} . $dest/ \;
        # """ % cpath
        # C = C.replace("$dest", destpath)
        # self._cuisine.core.run(C)
        #
        # lpath = j.sal.fs.joinPaths(cpath, "include",)
        # ldest = j.sal.fs.joinPaths(destpath, "include")
        # self._cuisine.core.copyTree(source=lpath, dest=ldest, keepsymlinks=False, deletefirst=False,
        #                             overwriteFiles=True,
        #                             recursive=True, rsyncdelete=True, createdir=True)

        print("BUILD COMPLETED OK")
