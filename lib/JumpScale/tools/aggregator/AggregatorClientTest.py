from JumpScale import j


class AggregatorClientTest(object):
    def __init__(self):
        self.redis = j.core.db

    def statstest(self):
        #simulate network statistics for X nr of network cards (throughput, errors, ...)
        #dump them raw in influxdb (will be our test set): put in separate DB
        #fetch through monitor client the stats object
        #double check that avg, max, ... works
        #also check that after e.g. 3min the avg are recalculated  
        #use influxdb dumper
        #test data from test DB with main DB, this way we can validate our results

        raise NotImplementedError()


    def logstest(self):
        #some fast perf test
        #get logs in & out
        #check we cannot put more values in redis as possible (the defense mechanismes)
        raise NotImplementedError()

    def ecotest(self):
        raise NotImplementedError()
        


