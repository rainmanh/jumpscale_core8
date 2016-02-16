from JumpScale import j
import Dumper
import collections


Stats = collections.namedtuple("Stats", "node key epoch stat avg max")


class InfluxDumper(Dumper.BaseDumper):
    QUEUE_MIN = 'queues:stats:min'
    QUEUE_HOUR = 'queues:stats:hour'
    QUEUES = [QUEUE_MIN, QUEUE_HOUR]

    def __init__(self, influx, database=None, cidr='127.0.0.1', port=7777):
        super(InfluxDumper, self).__init__(cidr, port)

        self.influxdb=influx

        if database is None:
            database = 'statistics'

        self.database = database
        found = False
        for db in self.influxdb.get_list_database():
            if db['name'] == database:
                found = True

        if not found:
            self.influxdb.create_database(database)

    def _parse_line(self, line):
        """
        Line is formated as:
        node|key|epoch|stat|avg|max
        :param line: Line to parse
        :return: Stats object
        """

        parts = line.split('|')
        if len(parts) != 6:
            raise Exception('Invalid stats line "%s"' % line)
        return Stats(parts[0], parts[1], int(parts[2]), float(parts[3]), float(parts[4]), float(parts[5]))

    def _dump(self, key, stats, info):
        tags = j.data.tags.getObject(info.get('tags', ''))

        points = [
            {
                "measurement": key,
                "tags": tags.tags,
                "time": stats.epoch,
                "fields": {
                    "value": stats.avg,
                    "max": stats.max,
                }
            }
        ]

        self.influxdb.write_points(points, database=self.database, time_precision='s')

    def _dump_hour(self, stats):
        print(stats)

    def dump(self, redis):
        """
        Process redis connection until the queue is empty, then return None
        :param redis:
        :return:
        """
        while True:
            data = redis.blpop(self.QUEUES, 1)
            if data is None:
                return

            queue, line = data
            queue = queue.decode()
            line = line.decode()

            stats = self._parse_line(line)
            info = redis.get("stats:%s:%s" % (stats.node, stats.key))

            if info is not None:
                info = j.data.serializer.json.loads(info)
            else:
                info = dict()

            if queue == self.QUEUE_MIN:
                self._dump("%s_%s_m" % (stats.node, stats.key), stats, info)
            else:
                self._dump("%s_%s_h" % (stats.node, stats.key), stats, info)
