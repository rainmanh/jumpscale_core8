from JumpScale import j
from NetworkScanner import NetworkScanner
import multiprocessing


class BaseDumper(object):
    def __init__(self, cidr, port=6379):
        self._cidr = cidr
        self._port = port

        scanner = NetworkScanner(cidr, port)
        self._candidates = scanner.scan()

    def start(self):
        queue = multiprocessing.Queue()
        for ip in self.candidates:
            queue.put_nowait(ip)

        pool = multiprocessing.Pool(4)

        while True:
            print("Getting new IP")
            ip = queue.get()
            print("Main: process ip %s", ip)
            pool.apply_async(self._process, (ip, queue))

    @property
    def cidr(self):
        return self._cidr

    @property
    def port(self):
        return self._port

    @property
    def candidates(self):
        return self._candidates

    def _process(self, ip, queue):
        print("Processing IP: %s" % ip)
        redis = j.clients.redis.getRedisClient(ip, self.port)
        try:
            self.dump(redis)
        finally:
            queue.put_nowait(ip)

    def dump(self, redis):
        raise NotImplementedError
