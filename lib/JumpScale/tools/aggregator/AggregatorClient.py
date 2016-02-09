from JumpScale import j
import time
import os

class AggregatorClient(object):
    def __init__(self, redis, nodename):
        self.redis = redis
        self._sha = dict()

        path = os.path.dirname(__file__)
        luapaths = j.sal.fs.listFilesInDir(path, recursive=False, filter="*.lua", followSymlinks=True)
        for luapath in luapaths:
            basename = j.sal.fs.getBaseName(luapath).replace(".lua", "")
            lua = j.sal.fs.fileGetContents(luapath)
            self._sha[basename] = self.redis.script_load(lua)

        self.nodename = nodename

    def measure(self, key, measurement, tags, value):
        """
        @param measurement is what you are measuring e.g. kbps (kbits per sec)
        @param key is well chosen location in a tree structure e.g. key="%s.%s.%s"%(self.nodename,dev,measurement) e.g. myserver.eth0.kbps
           key needs to be unique
        @param tags node:kds dim:iops location:elgouna  : this allows aggregation in influxdb level
        """
        return self._measure(key, measurement, tags, value, type="A")

    def measureDiff(self, key, measurement, tags, value):
        return self.measure(key, measurement, tags, value, type="D")

    def _measure(self, key, measurement, tags, value, type):
        """
        in redis:

        local key=KEYS[1]
        local measurement=ARGV[1]
        local value = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local type=ARGV[4]
        local tags=ARGV[5]
        local node=ARGV[6]

        """
        now = int(time.time() * 1000)  # millisecond
        res = self.redis.evalsha(self._sha["stat"], 1, key, measurement, value, str(now), type, tags, self.nodename)

        print("%s %s" % (key, res))

        return res

    def log(self, message, tags="", level=5, time=0):
        if time == 0:
            time = int(time.time() * 1000)
        # 1 means there is 1 key, others are args
        res = self.redis.evalsha(self._sha["logs"], 1, self.nodename, message, tags, str(level), str(time))

    def errorcondition(self, message, messagepub="", level=5, type="UNKNOWN", tags="", \
                       code="", funcname="", funcfilepath="", backtrace="", epoch=0):
        """
        @param type: "BUG", "PERF", "OPS", "UNKNOWN"), default="UNKNOWN"

        usage of tags (tags can be used in all flexibility to ad meaning to an errorondition)
        e.g. nid: gid: aid: pid: jid: mjid: appname: 
            nid = IntField()
            gid = IntField()    
            aid = IntField(default=0)
            pid = IntField(default=0)
            jid = StringField(default='')  #@todo (*2*) is this right, string???
            masterjid = IntField(default=0)  = mjid
            appname = StringField(default="")
            category = StringField(default="")


        core elements
            level = IntField(default=1, required=True)
            type = StringField(choices=("BUG", "PERF", "OPS", "UNKNOWN"), default="UNKNOWN", required=True)
            state = StringField(choices=("NEW", "ALERT", "CLOSED"), default="NEW", required=True)
            errormessage = StringField(default="")
            errormessagePub = StringField(default="")  # StringField()
            tags = StringField(default="")
            code = StringField()
            funcname = StringField(default="")
            funcfilepath = StringField(default="")
            backtrace = StringField()
            lasttime = IntField(default=j.data.time.getTimeEpoch())
            closetime = IntField(default=0)
            occurrences = IntField(default=0)
        """
        if time == 0:
            time = int(time.time() * 1000)
        # 1 means there is 1 key, others are args
        res = self.redis.evalsha(self._sha["eco"], 1, message, messagepub, str(level), type, \
                                 tags, code, funcname, funcfilepath, backtrace, str(time))

    def statGet(self, key):
        """
        key is e.g. mynode.sda1.iops
        """
        data = self.redis.hget("stats:%s" % self.nodename, key)
        if data == None:
            return {"val": None}
        data = j.data.serializer.json.loads(data)
        return data

    @property
    def stats(self):
        """
        iterator to go over stat objects
        """
        # @todo

    def logGet(self):
        """
        get oldest log object from queue & return as dict
        """
        # @todo ...
        return data

    @property
    def logs(self):
        """
        iterator to go over log objects (oldest first)
        """
        # @todo

    def ecoGet(self, key="", removeFromQueue=True):
        """
        get errorcondition object from queue & return as dict
        if key not specified then get oldest ECO object & remove from queue if removeFromQueue is set
        if key set, do not remove from queue
        """
        # @todo ...
        return data

    @property
    def ecos(self):
        """
        iterator to go over errorcondition objects (oldest first)
        """
        # @todo

    def reality(self, key, json, modeltype="", tags="", time=0, ):
        """
        anything found on local node worth mentioning to central env e.g. disk information, network information
        each piece of info gets a well chosen key e.g. disk.sda1

        an easy way to structure the objects well is to use our model layer see:

        objects worth filling in:
        - j.data.models.system.Node()
        - j.data.models.system.Machine()
        - j.data.models.system.Nic()
        - j.data.models.system.Process()
        - j.data.models.system.VDisk()
        - disk=j.data.models.system.Disk()

        to then get the json do:
            disk.to_json()

        @param modeltype defines which model has been used e.g. VDisk this allows the dumper to get the right model & insert in the right way in mongodb

        """
        if time == 0:
            time = int(time.time() * 1000)
        # 1 means there is 1 key, others are args
        res = self.redis.evalsha(self._sha["reality"], 1, key, json, self.nodename, tags, str(time), modeltype)

    def realityGet(self, key="", removeFromQueue=True):
        """
        if key not specified then get oldest object & remove from queue if removeFromQueue is set
        if key set, do not remove from queue        
        """

    @property
    def realities(self):
        """
        iterator to go over reality objects (oldest first)
        """
        # @todo
