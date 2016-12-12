from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineVulcand(app):
    NAME = "vulcand"

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def build(self, reset=False):
        if reset is False and self.isInstalled():
            return
        C = '''
        #!/bin/bash
        set -e
        source /bd_build/buildconfig
        set -x

        export goDir=$TMPDIR/vulcandgoDir

        if [ ! -d $GODIR ]; then
            mkdir -p $GODIR
        fi

        go get -d github.com/vulcand/vulcand

        cd $GODIR/src/github.com/vulcand/vulcand
        CGO_ENABLED=0 go build -a -ldflags '-s' -installsuffix nocgo .
        GOOS=linux go build -a -tags netgo -installsuffix cgo -ldflags '-w' -o ./vulcand .
        GOOS=linux go build -a -tags netgo -installsuffix cgo -ldflags '-w' -o ./vctl/vctl ./vctl
        GOOS=linux go build -a -tags netgo -installsuffix cgo -ldflags '-w' -o ./vbundle/vbundle ./vbundle

        mkdir -p /build/vulcand
        cp $GODIR/src/github.com/vulcand/vulcand/vulcand $BASEDIR/bin/
        cp $GODIR/src/github.com/vulcand/vulcand/vctl/vctl $BASEDIR/bin/
        cp $GODIR/src/github.com/vulcand/vulcand/vbundle/vbundle $BASEDIR/bin/

        rm -rf $GODIR

        '''
        C = self._cuisine.bash.replaceEnvironInText(C)
        self._cuisine.core.execute_bash(C, profile=True)
        self._cuisine.bash.addPath("$BASEDIR/bin")
