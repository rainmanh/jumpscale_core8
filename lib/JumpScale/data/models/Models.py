
from mongoengine import *
from JumpScale import j
import json
import uuid


class ModelBase(Document):
    guid = StringField(default=lambda: str(uuid.uuid4()))
    gid = IntField(default=lambda: j.application.whoAmI.gid if j.application.whoAmI else 0)
    nid = IntField(default=lambda: j.application.whoAmI.nid if j.application.whoAmI else 0)
    epoch = IntField(default=j.tools.time.getTimeEpoch)
    meta = {'allow_inheritance': True}

    def to_dict(self):
        d = json.loads(ModelBase.to_json(self))
        d.pop("_cls")
        if "_id" in d:
            d.pop("_id")
        if "_redis" in d:
            d.pop("_redis")
        return d

    @classmethod
    def find(cls, query, redis=False):
        if redis:
            raise RuntimeError("not implemented")
        else:
            return cls.objects(__raw__=query)

    def save(self):
        if "_redis" in self.__dict__:
            redis = True
            return j.data.models.set(self, redis=redis)
        else:
            redis = False
            return super(ModelBase, self).save()

    def __str__(self):
        return (json.dumps(self.to_dict(), sort_keys=True, indent=4))

    __repr__ = __str__


class ModelErrorCondition(ModelBase):
    aid = IntField(default=0)
    pid = IntField(default=0)
    jid = IntField(default=0)
    masterjid = IntField(default=0)
    appname = StringField(default="")
    level = StringField(choices=("CRITICAL","MAJOR","WARNING","INFO"), default="CRITICAL", required=True)
    type = StringField(choices=("BUG","PERF","OPS","UNKNOWN"), default="UNKNOWN", required=True)
    state = StringField(choices=("NEW","ALERT","CLOSED"), default="NEW", required=True)
    # StringField() <--- available starting version 0.9
    errormessage = StringField()
    errormessagePub = StringField()  # StringField()
    category = StringField(default="")
    tags = StringField(default="")
    code = StringField()
    funcname = StringField(default="")
    funcfilename = StringField(default="")
    funclinenr = IntField(default=0)
    backtrace = StringField()
    backtraceDetailed = StringField()
    extra = StringField()
    lasttime = IntField(default=0)
    closetime = IntField(default=0)
    occurrences = IntField(default=0)


class ModelGrid(ModelBase):
    name = StringField(default='master')
    #  id = IntField(default=1)


class ModelGroup(ModelBase):
    name = StringField(default='')
    domain = StringField(default='')
    gid = IntField(default=1)
    roles = ListField(StringField())
    active = BooleanField(default=True)
    description = StringField(default='master')
    lastcheck = IntField(default=j.tools.time.getTimeEpoch())
    users = ListField(StringField())


class ModelJob(EmbeddedDocument):
    nid = IntField(required=True)
    gid = IntField(required=True)
    data = StringField(default='')
    streams = ListField(StringField())
    level = IntField()
    state = StringField(required=True, choices=('SUCCESS', 'ERROR', 'TIMEOUT', 'KILLED', 'QUEUED', 'RUNNING'))
    starttime = IntField()
    time = IntField()
    tags = StringField()
    critical = StringField()

    meta = {
        'indexes': [{'fields': ['epoch'], 'expireAfterSeconds': 3600 * 24 * 5}],
        'allow_inheritance': True
    }


class ModelCommand(ModelBase):
    gid = IntField(default=0)
    nid = IntField(default=0)
    cmd = StringField()
    roles = ListField(StringField())
    fanout = BooleanField(default=False)
    args = DictField()
    data = StringField()
    tags = StringField()
    starttime = IntField()
    jobs = ListField(EmbeddedDocumentField(ModelJob))


class ModelAudit(ModelBase):
    user = StringField(default='')
    result = StringField(default='')
    call = StringField(default='')
    status_code = StringField(default='')
    args = StringField(default='')
    kwargs = StringField(default='')
    timestamp = StringField(default='')
    meta = {'indexes': [
        {'fields': ['epoch'], 'expireAfterSeconds': 3600 * 24 * 5}
    ], 'allow_inheritance': True}

class ModelDisk(ModelBase):
    partnr = IntField()
    gid = IntField()
    nid = IntField()
    path = StringField(default='')
    size = IntField()
    free = IntField()
    ssd = IntField()
    fs = StringField(default='')
    mounted = BooleanField()
    mountpoint = StringField(default='')
    active = BooleanField()
    model = StringField(default='')
    description = StringField(default='')
    type = ListField(StringField())  # BOOT, DATA, ...
    # epoch of last time the info was checked from reality
    lastcheck = IntField(default=j.tools.time.getTimeEpoch())


class ModelAlert(ModelBase):
    gid = IntField()
    nid = IntField()
    username = StringField(default='')
    description = StringField(default='')
    descriptionpub = StringField(default='')
    level = IntField(min_value=1, max_value=3)
    # dot notation e.g. machine.start.failed
    category = StringField(default='')
    tags = StringField(default='')  # e.g. machine:2323
    state = StringField(choices=("NEW","ALERT","CLOSED"), default='NEW', required=True)
    history = ListField(DictField())
    # first time there was an error condition linked to this alert
    inittime = IntField(default=j.tools.time.getTimeEpoch())
    # last time there was an error condition linked to this alert
    lasttime = IntField()
    closetime = IntField()  # alert is closed, no longer active
    # $nr of times this error condition happened
    nrerrorconditions = IntField()
    errorconditions = ListField(IntField())  # ids of errorconditions


class ModelHeartbeat(ModelBase):

    """
    """
    nid = IntField()
    gid = IntField()
    lastcheck = IntField(default=j.tools.time.getTimeEpoch())


class ModelJumpscript(ModelBase):
    id = IntField()
    gid = IntField()
    name = StringField(default='')
    descr = StringField(default='')
    category = StringField(default='')
    organization = StringField(default='')
    author = StringField(default='')
    license = StringField(default='')
    version = StringField(default='')
    roles = ListField(StringField())
    action = StringField(default='')
    source = StringField(default='')
    path = StringField(default='')
    args = ListField(StringField())
    enabled = BooleanField()
    async = BooleanField()
    period = IntField()
    order = IntField()
    queue = StringField(default='')
    log = BooleanField()


class ModelMachine(ModelBase):
    gid = IntField()
    nid = IntField()
    name = StringField(default='')
    roles = ListField(StringField())
    netaddr = StringField(default='')
    ipaddr = ListField(StringField())
    active = BooleanField()
    # STARTED,STOPPED,RUNNING,FROZEN,CONFIGURED,DELETED
    state = StringField(choices=("STARTED","STOPPED","RUNNING","FROZEN","CONFIGURED","DELETED"), default='', required=True)
    mem = IntField()  # $in MB
    cpucore = IntField()
    description = StringField(default='')
    otherid = StringField(default='')
    type = StringField(default='')  # VM,LXC
    # epoch of last time the info was checked from reality
    lastcheck = IntField(default=j.tools.time.getTimeEpoch())


class ModelNic(ModelBase):
    gid = IntField()
    nid = IntField()
    name = StringField(default='')
    mac = StringField(default='')
    ipaddr = ListField(StringField())
    active = BooleanField(default=True)
    # poch of last time the info was checked from reality
    lastcheck = IntField(default=j.tools.time.getTimeEpoch())


class ModelNode(ModelBase):
    gid = IntField()
    name = StringField(default='')
    roles = ListField(StringField())
    netaddr = StringField(default='')
    machineguid = StringField(default='')
    ipaddr = ListField(StringField())
    active = BooleanField()
    peer_stats = IntField()  # node which has stats for this node
    # node which has transactionlog or other logs for this node
    peer_log = IntField()
    peer_backup = IntField()  # node which has backups for this node
    description = StringField(default='')
    lastcheck = IntField(default=j.tools.time.getTimeEpoch())
    # osisrootobj,$namespace,$category,$version
    _meta = ListField(StringField())


class ModelProcess(ModelBase):
    gid = IntField()
    nid = IntField()
    aysdomain = StringField(default='')
    aysname = StringField(default='')
    pname = StringField(default='')  # process name
    sname = StringField(default='')  # name as specified in startup manager
    ports = ListField(IntField())
    instance = StringField(default='')
    systempid = ListField(IntField())  # system process id (PID) at this point
    epochstart = IntField()
    epochstop = IntField()
    active = BooleanField()
    lastcheck = IntField(default=j.tools.time.getTimeEpoch())
    cmd = StringField(default='')
    workingdir = StringField(default='')
    parent = StringField(default='')
    type = StringField(default='')
    statkey = StringField(default='')
    nr_file_descriptors = FloatField()
    nr_ctx_switches_voluntary = FloatField()
    nr_ctx_switches_involuntary = FloatField()
    nr_threads = FloatField()
    cpu_time_user = FloatField()
    cpu_time_system = FloatField()
    cpu_percent = FloatField()
    mem_vms = FloatField()
    mem_rss = FloatField()
    io_read_count = FloatField()
    io_write_count = FloatField()
    io_read_bytes = FloatField()
    io_write_bytes = FloatField()
    nr_connections_in = FloatField()
    nr_connections_out = FloatField()


class ModelTest(ModelBase):
    gid = IntField()
    nid = IntField()
    name = StringField(default='')
    testrun = StringField(default='')
    path = StringField(default='')
    state = StringField(choices=("OK","ERROR","DISABLED"), default='', required=True)
    priority = IntField()  # lower is highest priority
    organization = StringField(default='')
    author = StringField(default='')
    version = IntField()
    categories = ListField(StringField())
    starttime = IntField(default=j.tools.time.getTimeEpoch())
    endtime = IntField()
    enable = BooleanField()
    result = DictField()
    output = DictField(default='')
    eco = DictField(default='')
    license = StringField(default='')
    source = DictField(default='')


class ModelUser(ModelBase):
    name = StringField(default='')
    domain = StringField(default='')
    passwd = StringField(default='')  # stored hashed
    roles = ListField(StringField())
    active = BooleanField()
    description = StringField(default='')
    emails = ListField(StringField())
    xmpp = ListField(StringField())
    mobile = ListField(StringField())
    # epoch of last time the info updated
    lastcheck = IntField(default=j.tools.time.getTimeEpoch())
    groups = ListField(StringField())
    authkey = StringField(default='')
    data = StringField(default='')
    authkeys = ListField(StringField())


class ModelSessionCache(ModelBase):
    user = StringField()
    _creation_time = IntField(default=j.tools.time.getTimeEpoch())
    _accessed_time = IntField(default=j.tools.time.getTimeEpoch())
    meta = {'indexes': [
        {'fields': ['epoch'], 'expireAfterSeconds': 432000}
    ], 'allow_inheritance': True}


# @todo complete ASAP all from https://github.com/Jumpscale/jumpscale_core8/blob/master/apps/osis/logic/system/model.spec  (***)

# o=ModelJob()
# o.clean()

# from IPython import embed
# embed()

# pi

# o.save()
