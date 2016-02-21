from JumpScale import j
import psutil

descr = """
gather network statistics
"""

organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
category = "info.gather.nic"
period = 60 #always in sec
timeout = period * 0.2
enable=True
async=True
queue='process'
roles = []
log=False

def action():
    import statsd
    stats = statsd.StatsClient()
    pipe = stats.pipeline()
    hostname =j.sal.nettools.getHostname()
    aggregator = j.tools.aggregator.getClient(j.core.db,  hostname)
    counters=psutil.net_io_counters(True)
    pattern = None
    if j.application.config.exists('gridmonitoring.nic.pattern'):
        pattern = j.application.config.getStr('gridmonitoring.nic.pattern')

    for nic, stat in counters.items():
        if pattern and j.codetools.regex.match(pattern,nic) == False:
            continue
        if j.sal.nettools.getNicType(nic) == 'VIRTUAL' and not 'pub' in nic:
            continue
        result = dict()
        bytes_sent, bytes_recv, packets_sent, packets_recv, errin, errout, dropin, dropout = stat
        result['kbytes.sent'] = int(round(bytes_sent/1024.0,0))
        result['kbytes.recv'] = int(round(bytes_recv/1024.0,0))
        result['packets.sent'] = packets_sent
        result['packets.recv'] = packets_recv
        result['error.in'] = errin
        result['error.out'] = errout
        result['drop.in'] = dropin
        result['drop.out'] = dropout
        for key, value in result.items():
            pipe.gauge("%s_%s_nic_%s_%s" % (j.application.whoAmI.gid, j.application.whoAmI.nid, nic, key), value)

            aggregator.measure(tags={'nid': j.application.whoAmI.nid, 'gid': j.application.whoAmI.gid} ,key="network.%s" %key, value=value, measurement="")

    pipe.send()

if __name__ == '__main__':
    action()
