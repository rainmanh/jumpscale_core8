from JumpScale import j

from InfluxDumper import InfluxDumper
from AggregatorClient import AggregatorClient
from AggregatorClientTest import AggregatorClientTest


class Aggregator(object):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.aggregator"
        self.nodes = []

    def getClient(self, redisConnection, nodename):
        return AggregatorClient(redisConnection, nodename)

    def influxpump(self, influxdb, port=7777):
        """
        will dump redis stats into influxdb(s)
        get connections from j.jumpscale.clients...
        """

        d = InfluxDumper(influxdb, port=port)
        d.start()

    def monogopump(self, redisConnections, mongodbConnections):
        """
        will dump redis stats into influxdb(s)
        get connections from j.jumpscale.clients...
        """

        d = MongoDumper(redisConnections, mongodbConnections)
        d.start()

    def test(self):
        # ... @todo (*1*)
        cl = MonitorClientTest()
