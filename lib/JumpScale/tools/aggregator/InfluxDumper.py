from JumpScale import j

# import sys
import time

# import os
import psutil


class InfluxDumper():

    def __init__(self,redisConnections,influxdbConnections):
        self.redisConnections=redisConnections
        self.influxdbConnections=influxdbConnections

        for eachDB in ...:
            try:
                self.influxdb.drop_database(testname)
            except:
                pass
            self.influxdb.create_database(testname)
            self.influxdb.switch_database(testname)
            self._statObjects={}

    def getStatObjectInfo(self,redis,node,key):
        key2="%s_%s"%(node,key)
        if not key2 in self._statObjects:
            cl=j.tools.redistools.getMonitorClient(redis,node)        
            data=cl.getStatObject(key) #get the other info like tags from redis
            #why do we do this???
            data["tags"]="%s key:%s"%(data["tags"].strip(),key)
            data["tags"]=data["tags"].replace(" ",",")
            data["tags"]=data["tags"].replace(":","=")
            self._statObjects[key2]=data
        return self._statObjects[key2]
        

    def start(self):
        q='queues:stats'
        start=time.time()
        counter=0
        data=""
        while True:
            for redis in self.redisConnections:
                res=redis.lpop(q)            
                while res!=None:
                    counter+=1
                    # print res
                    node,key,epoch,last,mavg,mmax,havg,hmax=res.split("|")
                    data=self.getStatObjectInfo(redis,node,key)
                    tags=data["tags"]
                    last=int(last)
                    #is BUG, but for now to be able to continue
                    #@todo (*2*) fix this and check it all
                    if last<1000000:
                        data+="%s,%s value=%s %s\n"%(measurement,tags,last,epoch)
                    else:
                        print("SKIPPED:%s"%"%s,%s value=%s %s\n"%(measurement,tags,last,epoch))

                    if counter>100 or time.time()>start+2:
                        start=time.time()
                        counter=0                                            
                        print(data)
                        j.clients.influxdb.postraw(data,host='localhost', port=8086,username='root', password='root', database=self.dbname)
                        # print "dump done to db:%s"%self.dbname                        
                        data=""                    
                    
                    res=redis.lpop(q)

            time.sleep(1)            
