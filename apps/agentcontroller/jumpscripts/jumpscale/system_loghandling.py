from JumpScale import j

descr = """
process logs queued in redis
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "log.handling.init"

timeout = 4
startatboot = True
order = 1
enable = True
async = True
queue ='process'
log = False
roles = []

try:
    import ujson as json
except:
    import json

import time

def action():

    rediscl = j.clients.redis.getByInstance("system")
    logqueue = rediscl.getQueue('logs')
    ecoqueue = rediscl.getQueue('eco')

    clientLogger = j.data.models.system.Log
    clientEco = j.data.models.system.Errorcondition

    log = None
    path = "%s/apps/processmanager/loghandling/"%j.dirs.baseDir
    if j.sal.fs.exists(path=path):
        loghandlingTE = j.core.taskletengine.get(path)
        log=logqueue.get_nowait()
        # j.core.grid.logger.osis = OSISclientLogger
    else:
        loghandlingTE = None

    ecoguid = None
    path = "%s/apps/processmanager/eventhandling"%j.dirs.baseDir
    if j.sal.fs.exists(path=path):
        eventhandlingTE = j.core.taskletengine.get(path)
        ecoguid=ecoqueue.get_nowait()
    else:
        eventhandlingTE = None

    out=[]
    while log != None:
        log2=json.decode(log)
        log3 = j.logger.getLogObjectFromDict(log2)
        log4= loghandlingTE.executeV2(logobj=log3)
        if log4 != None:
            clientLogger.save(log4.__dict__)
        log=logqueue.get_nowait()

    while ecoguid != None:
        eco = j.data.models.system.Errorcondition.find({'guid':ecoguid})
        if eco:
            eco = eco[0].to_dict
            if not eco.get('epoch'):
                eco["epoch"] = int(time.time())
            ecoobj = j.errorconditionhandler.getErrorConditionObject(ddict=eco)
            ecores= eventhandlingTE.executeV2(eco=ecoobj)
            if hasattr(ecores,"tb"):
                ecores.__dict__.pop("tb")
            clientEco.save(ecores.__dict__)
            ecoguid=ecoqueue.get_nowait()

if __name__ == '__main__':
    action()

