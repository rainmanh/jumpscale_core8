from JumpScale import j
from NetworkScanner import NetworkScanner
import multiprocessing
import time
import logging


class BaseDumper(object):
    def __init__(self, cidr, port=6379):
        logging.root.setLevel(logging.INFO)

        self._cidr = cidr
        self._port = port

        scanner = NetworkScanner(cidr, port)
        self._candidates = scanner.scan()

    def start(self):
        manager = multiprocessing.Manager()
        queue = manager.Queue()
        for ip in self.candidates:
            queue.put_nowait(ip)

        pool = multiprocessing.Pool(4)

        while True:
            ip = queue.get()
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
        redis = j.clients.redis.getRedisClient(ip, self.port)
        now = int(time.time())
        try:
            logging.info("Processing redis %s" % ip)
            self.dump(redis)
        except Exception:
            logging.exception("Failed to process redis '%s'" % ip)
        finally:
            # workers must have some rest (1 sec) before moving to next
            # ip to process
            if int(time.time()) - now < 1:
                # process took very short time. Give worker time to rest
                time.sleep(1)

            queue.put_nowait(ip)

    def dump(self, redis):
        """
        Dump, gets a redis connection. It must process the queues of redis until there is no more items to
        process and then immediately return.

        :param redis: redis connection
        :return:
        """
        """
        :param redis:
        :return:
        """
        raise NotImplementedError
