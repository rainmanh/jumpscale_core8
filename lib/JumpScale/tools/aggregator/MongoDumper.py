from JumpScale import j

import time


class MongoDumper():

    def __init__(self,redisConnections,mongodbConnections):
        self.redisConnections=redisConnections
        self.mongodbConnections=mongodbConnections
        self.processLogs=False

    def start(self):
        """
        use the queues to get logs & ecos & reality objects
        put them (indexed!) in specified mongodb(s)
        """
        ...

        #for eco & reality objects make sure j.data.models is used to recreate the mongoengine object before inserting in the mongodb database
        #logs we can probably do direct because will go faster then, speed here is of the essence