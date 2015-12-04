
from mongoengine import *
from JumpScale import j
import json


class ModelBase(Document):
    guid = StringField(default="")
    id = StringField(default="")
    gid = IntField(default=0)
    nid = IntField(default=0)
    epoch = IntField(default=0)
    meta = {'allow_inheritance': True}

    def clean(self):
        if self.guid == "":
            self.guid = j.base.idgenerator.generateXCharID(6)

        if self.id == "":
            self.id = self.guid


        if self.epoch == 0:
            self.epoch = j.base.time.getTimeEpoch()
        if j.application.whoAmI != None:
            if self.gid == 0:
                self.gid = j.application.whoAmI.gid
            if self.nid == 0:
                self.nid = j.application.whoAmI.nid
            # if self.pid == 0:
            #     self.pid = j.application.whoAmI.pid

    def to_dict(self):
        d=json.loads(ModelBase.to_json(self))
        d.pop("_id")
        d.pop("_cls")
        return d

    def save(self):
        j.core.models.set(self)
        

    def __str__(self):
        return (json.dumps(json.loads(self.to_json()), sort_keys=True, indent=4))

    __repr__ = __str__


class ModelErrorCondition(ModelBase):
    aid = IntField(default=0)
    pid = IntField(default=0)
    jid = IntField(default=0)
    masterjid = IntField(default=0)
    appname = StringField(default="")
    level = StringField(default="CRITICAL")
    type = StringField(default="UNKNOWN")
    state = StringField(default="NEW")  # ["NEW","ALERT","CLOSED"]:
    errormessage = MultiLineStringField()
    errormessagePub = MultiLineStringField()
    category = StringField(default="")
    tags = StringField(default="")
    code = MultiLineStringField()
    funcname = StringField(default="")
    funcfilename = StringField(default="")
    funclinenr = IntField(default=0)
    backtrace = MultiLineStringField()
    backtraceDetailed = MultiLineStringField()
    extra = MultiLineStringField()
    lasttime = IntField(default=0)
    closetime = IntField(default=0)
    occurrences = IntField(default=0)

    def clean(self):
        ModelBase.clean(self)
        if self.lasttime == 0:
            self.lasttime = j.base.time.getTimeEpoch()
        if self.state not in ["NEW", "ALERT", "CLOSED"]:
            raise ValidationError("State can only be NEW,ALERT or CLOSED")
        if self.type not in ["BUG", "PERF", "OPS", "UNKNOWN"]:
            raise ValidationError("State can only be NEW,ALERT or CLOSED")
        if self.level not in ["CRITICAL", "MAJOR", "WARNING", "INFO"]:
            raise ValidationError("State can only be CRITICAL,MAJOR,WARNING,INFO")


class ModelGrid(ModelBase):
    name = StringField(default='master')
    #  id = IntField(default=1)


class ModelGroup(ModelBase):
    domain = StringField(default='')
    gid = IntField(default=1)
    roles = ListField(StringField())
    active = BooleanField(default=1)
    description = StringField(default='master')
    lastcheck = IntField(default=j.base.time.getTimeEpoch())
    users = ListField(StringField())


class ModelJob(ModelBase):
    sessionid = IntField()
    nid = IntField()
    gid = IntField()
    cmd = StringField(default='')
    wait = BooleanField(default=1)
    category = StringField(default='')
    roles = ListField(StringField())
    args = StringField(default='')
    queue = StringField(default='')
    timeout = IntField()
    result = StringField(default='')
    parent = IntField()
    resultcode = StringField(default='')
    # SCHEDULED,STARTED,ERROR,OK,NOWORK
    state = StringField(default='SCHEDULED')
    timeStart = IntField(default=j.base.time.getTimeEpoch())
    timeStop = IntField()
    log = BooleanField(default=1)
    errorreport = BooleanField(default=1)
    meta = {'indexes': [
                {'fields': ['epoch'], 'expireAfterSeconds': 3600 * 24 * 5}
           ], 'allow_inheritance': True}

    def clean(self):
        ModelBase.clean(self)
        if self.state not in ["SCHEDULED", "STARTED", "ERROR", "OK", "NOWORK"]:
            raise ValidationError("State can only be SCHEDULED, STARTED, ERROR, OK or NOWORK")


class ModelAudit(ModelBase):
    user = StringField(default='')
    result = StringField(default='')
    call = StringField(default='')
    statuscode = StringField(default='')
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
    lastcheck = IntField(default=j.base.time.getTimeEpoch())


class ModelAlert(ModelBase):
    gid = IntField()
    nid = IntField()
    description = StringField(default='')
    descriptionpub = StringField(default='')
    level = IntField()  # 1:critical, 2:warning, 3:info
    # dot notation e.g. machine.start.failed
    category = StringField(default='')
    tags = StringField(default='')  # e.g. machine:2323
    state = StringField(default='')  # ["NEW","ALERT","CLOSED"]
    # first time there was an error condition linked to this alert
    inittime = IntField(default=j.base.time.getTimeEpoch())
    # last time there was an error condition linked to this alert
    lasttime = IntField()
    closetime = IntField()  # alert is closed, no longer active
    # $nr of times this error condition happened
    nrerrorconditions = IntField()
    errorconditions = ListField(IntField())  # ids of errorconditions

    def clean(self):
        ModelBase.clean(self)
        if self.level not in [1, 2, 3]:
            raise ValidationError("Level can only be 1(critical), 2(warning) or 3(info)")
        if self.state not in ["NEW", "ALERT", "CLOSED"]:
            raise ValidationError('State can only be "NEW","ALERT" or "CLOSED"')


class ModelHeartbeat(ModelBase):

    """
    """
    nid = IntField()
    gid = IntField()
    lastcheck = IntField(default=j.base.time.getTimeEpoch())


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
    state = StringField(default='')
    mem = IntField()  # $in MB
    cpucore = IntField()
    description = StringField(default='')
    otherid = StringField(default='')
    type = StringField(default='')  # VM,LXC
    # epoch of last time the info was checked from reality
    lastcheck = IntField(default=j.base.time.getTimeEpoch())

    def clean(self):
        ModelBase.clean(self)
        if self.state not in ["STARTED", "STOPPED", "RUNNING", "FROZEN", "CONFIGURED", "DELETED"]:
            raise ValidationError('State can only be "STARTED", "STOPPED", "RUNNING", "FROZEN", "CONFIGURED" or "DELETED"')


class ModelNic(ModelBase):
    gid = IntField()
    nid = IntField()
    name = StringField(default='')
    mac = StringField(default='')
    ipaddr = ListField(StringField())
    active = BooleanField(default=1)
    # poch of last time the info was checked from reality
    lastcheck = IntField(default=j.base.time.getTimeEpoch())


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
    lastcheck = IntField(default=j.base.time.getTimeEpoch())
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
    lastcheck = IntField(default=j.base.time.getTimeEpoch())
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
    state = StringField(default='')  # OK, ERROR, DISABLED
    priority = IntField()  # lower is highest priority
    organization = StringField(default='')
    author = StringField(default='')
    version = IntField()
    categories = ListField(StringField())
    starttime = IntField(default=j.base.time.getTimeEpoch())
    endtime = IntField()
    enable = BooleanField()
    result = DictField()
    output = DictField(default='')
    eco = DictField(default='')
    license = StringField(default='')
    source = DictField(default='')

    def clean(self):
        ModelBase.clean(self)
        if self.state not in ["OK", "ERROR", "DISABLED"]:
            raise ValidationError('State can only be OK, ERROR or DISABLED')


class ModelUser(ModelBase):
    domain = StringField(default='')
    gid = IntField()
    passwd = StringField(default='')  # stored hashed
    roles = ListField(StringField())
    active = BooleanField()
    description = StringField(default='')
    emails = ListField(StringField())
    xmpp = ListField(StringField())
    mobile = ListField(StringField())
    lastcheck = IntField(default=j.base.time.getTimeEpoch())  # epoch of last time the info updated
    groups = ListField(StringField())
    authkey = StringField(default='')
    data = StringField(default='')
    authkeys = ListField(StringField())


# @todo complete ASAP all from https://github.com/Jumpscale/jumpscale_core7/blob/master/apps/osis/logic/system/model.spec  (***)

# o=ModelJob()
# o.clean()

# from IPython import embed
# embed()

# pi

# o.save()
