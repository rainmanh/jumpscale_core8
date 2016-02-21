from JumpScale import j

from InfluxDumper import InfluxDumper
from MongoDumper import MongoDumper
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

    def monogopump(self, port=7777):
        """
        will dump redis stats into influxdb(s)
        get connections from j.jumpscale.clients...
        """

        d = MongoDumper(port=port)
        d.start()

    def getTester(self):
        """
        The tester instance is used to test stats aggregation and more.

        Example usage:
        redis = j.clients.redis.getRedisClient('localhost', 6379)
        agg = j.tools.aggregator.getClient(redis, 'hostname')
        influx = j.clients.influxdb.get()
        tester = j.tools.aggregator.getTester()

        print(tester.statstest(agg, influx, 1000))

        this test should print something like

        ####################
        Minutes: 5
        Avg Sample Rate: 6224
        Test result: OK
        ####################
        Expected values:
        Sun Feb 21 09:56:27 2016: 516.612
        Sun Feb 21 09:57:27 2016: 505.787
        Sun Feb 21 09:58:27 2016: 401.824
        Sun Feb 21 09:59:27 2016: 397.15
        Sun Feb 21 10:00:27 2016: 497.779
        Reported values:
        Sun Feb 21 09:56:00 2016: 516.612
        Sun Feb 21 09:57:00 2016: 505.787
        Sun Feb 21 09:58:00 2016: 401.824
        Sun Feb 21 09:59:00 2016: 397.15
        Sun Feb 21 10:00:00 2016: 497.779
        ERRORS:
        No Errors

        :return: Report as string
        """
        return AggregatorClientTest()
