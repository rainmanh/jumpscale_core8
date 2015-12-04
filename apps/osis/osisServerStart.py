from JumpScale import j
import JumpScale.grid.osis
import time

j.application.start("osisserver")

import sys
if __name__ == '__main__':

    args=sys.argv
    osis_instance=args[1]
    osis = j.atyourservice.getService(role='osis', instance=osis_instance)
    # osishrd = j.application.getAppInstanceHRD(name="osis",instance=osis_instance)
    # connectionsconfig = osishrd.getDictFromPrefix('param.osis.connection')
    connections = {}
    # for dbname, instancename in connectionsconfig.items():
    dbs = ['mongodb', 'redis', 'influxdb']

    
    for dbname, services in list(osis.producers.items()):
        if dbname not in dbs:
            continue
        service = services[0]
        print(("connect to: %s"%dbname))

        if dbname=="mongodb":
            import JumpScale.grid.mongodbclient
            client=j.clients.mongodb.getByInstance(service.instance)

        elif dbname=="redis":
            import JumpScale.baselib.redis2
            while not j.clients.redis.isRunning(service.instance):
                time.sleep(0.1)
                print(("cannot connect to redis, will keep on trying forever, please start (%s)"%(service.instance)))
            client=j.clients.redis.getByInstance(service.instance)

        elif dbname=="influxdb":
            import JumpScale.baselib.influxdb2
            client = j.clients.influxdb.getByInstance(service.instance)
            databases = [db['name'] for db in client.get_list_database()]
            hrd = j.application.getAppInstanceHRD(instance=service.instance, name='influxdb_client')
            database_name = hrd.getStr('param.influxdb.client.dbname')
            if database_name not in databases:
                client.create_database(database_name)
            else:
                client.switch_database(database_name)
        connections["%s_%s"%(dbname,service.instance)]=client

    superadminpasswd = osis.hrd.get("param.osis.superadmin.passwd")

    j.core.osis.startDaemon(path="", overwriteHRD=False, overwriteImplementation=False, key="", port=5544, superadminpasswd=superadminpasswd, dbconnections=connections, hrd=osis.hrd)

    j.application.stop()
