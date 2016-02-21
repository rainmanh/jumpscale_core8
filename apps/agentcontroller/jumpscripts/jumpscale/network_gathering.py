from JumpScale import j
import psutil

descr = """
gather statistics about system
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "info.gather.nic"
period = 300 #always in sec
timeout = period * 0.2
enable=True
async=True
queue='process'
roles = []
log=False

def action():
    ncl = j.data.models.system.Nic
    netinfo = j.sal.nettools.getNetworkInfo()
    results = dict()
    pattern = None
    if j.application.config.exists('nic.pattern'):
        pattern = j.application.config.getStr('nic.pattern')
    import ipdb;ipdb.set_trace()
    for netitem in netinfo:
        name = netitem['name']
        if pattern and j.codetools.regex.match(pattern,name) == False:
            continue

        ipaddr = netitem.get('ip', [])

        nic = ncl()
        old = ncl.find({'name':name})

        results[name] = nic
        nic.active=True
        nic.gid = j.application.whoAmI.gid
        nic.nid = j.application.whoAmI.nid
        nic.ipaddr=ipaddr
        nic.mac=netitem['mac']
        nic.name = name

        if old:
            old_nic = old[0].to_dict()
            for key in ['name', 'active', 'gid', 'nid', 'ipaddr', 'mac', 'name']:
                if old_nic[key] != nic[key]:
                    print('Nic %s changed ' % name)
                    old[0].delete()
                    nic.save()
                    break


    nics = ncl.find({'nid': j.application.whoAmI.nid, 'gid': j.application.whoAmI.gid})
    #find deleted nices
    for nic in nics:
        nic_obj = nic.to_dict()
        if nic_obj['active'] and nic_obj['name'] not in results:
            #no longer active
            print ("NO LONGER ACTIVE:%s" % nic_obj['name'])
            nic_obj['active'] = False
            ncl.delete(nic)

if __name__ == '__main__':
    action()
