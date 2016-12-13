from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineSyncthing(app):

    NAME = 'syncthing'

    def build(self, start=True, install=True, reset=False):
        """
        build and setup syncthing to run on :8384 , this can be changed from the config file in /optvar/cfg/syncthing
        """
        # install golang
        if reset is False and self.isInstalled():
            return
        # self.cuisine.development.golang.install()

        # build
        url = "https://github.com/syncthing/syncthing.git"
        if self.cuisine.core.file_exists('$GODIR/src/github.com/syncthing/syncthing'):
            self.cuisine.core.dir_remove('$GODIR/src/github.com/syncthing/syncthing')
        dest = self.cuisine.development.git.pullRepo(url,
                                                     dest='$GODIR/src/github.com/syncthing/syncthing',
                                                     ssh=False,
                                                     depth=1)
        self.cuisine.core.run("cd %s && go run build.go -version v0.14.5 -no-upgrade" % dest, profile=True)

        if install:
            self.install(start)

    def install(self, start=True):
        """
        download, install, move files to appropriate places, and create relavent configs
        """
        # create config file
        config = """
        <configuration version="14">
            <folder id="default" path="$HOMEDIR/Sync" ro="false" rescanIntervalS="60" ignorePerms="false" autoNormalize="false">
                <device id="H7MBKSF-XNFETHA-2ERDXTB-JQCAXTA-BBTTLJN-23TN5BZ-4CL7KLS-FYCISAR"></device>
                <minDiskFreePct>1</minDiskFreePct>
                <versioning></versioning>
                <copiers>0</copiers>
                <pullers>0</pullers>
                <hashers>0</hashers>
                <order>random</order>
                <ignoreDelete>false</ignoreDelete>
            </folder>
            <device id="H7MBKSF-XNFETHA-2ERDXTB-JQCAXTA-BBTTLJN-23TN5BZ-4CL7KLS-FYCISAR" name="$hostname" compression="metadata" introducer="false">
                <address>dynamic</address>
            </device>
            <gui enabled="true" tls="false">
                <address>$lclAddrs:$port</address>
            </gui>
            <options>
                <listenAddress>tcp://0.0.0.0:22000</listenAddress>
                <globalAnnounceServer>default</globalAnnounceServer>
                <globalAnnounceEnabled>true</globalAnnounceEnabled>
                <localAnnounceEnabled>true</localAnnounceEnabled>
                <localAnnouncePort>21025</localAnnouncePort>
                <localAnnounceMCAddr>[ff32::5222]:21026</localAnnounceMCAddr>
                <maxSendKbps>0</maxSendKbps>
                <maxRecvKbps>0</maxRecvKbps>
                <reconnectionIntervalS>60</reconnectionIntervalS>
                <startBrowser>true</startBrowser>
                <upnpEnabled>true</upnpEnabled>
                <upnpLeaseMinutes>60</upnpLeaseMinutes>
                <upnpRenewalMinutes>30</upnpRenewalMinutes>
                <upnpTimeoutSeconds>10</upnpTimeoutSeconds>
                <urAccepted>0</urAccepted>
                <urUniqueID></urUniqueID>
                <restartOnWakeup>true</restartOnWakeup>
                <autoUpgradeIntervalH>12</autoUpgradeIntervalH>
                <keepTemporariesH>24</keepTemporariesH>
                <cacheIgnoredFiles>true</cacheIgnoredFiles>
                <progressUpdateIntervalS>5</progressUpdateIntervalS>
                <symlinksEnabled>true</symlinksEnabled>
                <limitBandwidthInLan>false</limitBandwidthInLan>
                <databaseBlockCacheMiB>0</databaseBlockCacheMiB>
                <pingTimeoutS>30</pingTimeoutS>
                <pingIdleTimeS>60</pingIdleTimeS>
                <minHomeDiskFreePct>1</minHomeDiskFreePct>
            </options>
        </configuration>
        """
        # install deps
        self.cuisine.development.golang.install()

        # create config file
        content = self.replace(config)
        content = content.replace('$lclAddrs', '0.0.0.0', 1)
        content = content.replace('$port', '18384', 1)

        self.cuisine.core.dir_ensure("$TEMPLATEDIR/cfg/syncthing/")
        self.cuisine.core.file_write("$TEMPLATEDIR/cfg/syncthing/config.xml", content)

        # If syncthing isn't found, it means that syncthing must be built first
        if not self.cuisine.core.file_exists('$BINDIR/syncthing'):
            self.cuisine.core.file_copy(source="$GODIR/src/github.com/syncthing/syncthing/bin/syncthing",
                                        dest="$BINDIR",
                                        recursive=True,
                                        overwrite=False)
        if start:
            self.start()

    def start(self):
        self.cuisine.core.dir_ensure("$JSCFGDIR")
        self.cuisine.core.file_copy("$TEMPLATEDIR/cfg/syncthing/", "$JSCFGDIR", recursive=True)
        pm = self.cuisine.processmanager.get("tmux")
        pm.ensure(name="syncthing", cmd="./syncthing -home  $JSCFGDIR/syncthing", path="$BINDIR")

    def stop(self):
        pm = self.cuisine.processmanager.get("tmux")
        pm.stop("syncthing")

    def restart(self):
        self.stop()
        self.start()
