from JumpScale import j

import logging
import logging.handlers
from colorlog import ColoredFormatter
import os


FILE_FORMAT = '%(asctime)s - %(pathname)s:%(lineno)d - %(levelname)-8s - %(message)s'
CONSOLE_FORMAT = '%(cyan)s[%(asctime)s]%(reset)s - %(pathname)s:%(lineno)-2d - %(log_color)s%(levelname)-8s%(reset)s - %(message)s'

js_log_level = {
    "CRITICAL":	50,
    "ERROR":	40,
    "WARNING":	30,
    # "PRINT":    25,
    "INFO":	    20,
    "DEBUG":	10,
    "NOTSET":	0,
}


class LoggerFactory:

    def __init__(self):
        self.__jslocation__ = "j.logger"

        # Associate 'name' with 'level'.
        # This is used when converting levels to text during message formatting.
        for name, level in js_log_level.items():
            self.__setattr__(name, level)
            logging.addLevelName(level, name)
        self.root_logger_name = 'j'

        self.handlers = {
            "console": self.__consoleHandler(),
            "file": self.__fileRotateHandler(),
        }
        # logging.basicConfig(level=logging.NOTSET, handlers=self.handlers.values())
        logging.setLoggerClass(JSLogger)
        self._logger = logging.getLogger(self.root_logger_name)
        self._logger.setLevel(logging.DEBUG)
        for h in self.handlers.values():
            self._logger.addHandler(h)

    def __fileRotateHandler(self, name='jumpscale'):
        # filename = os.path.join(j.dirs.logDir, "%s.log" % name)
        filename = "/optvar/log/%s.log" % name  # TODO can't use j.dirs here before j.dirs is loaded.
        formatter = logging.Formatter(FILE_FORMAT)
        fh = logging.handlers.TimedRotatingFileHandler(filename, when='D', interval=1, backupCount=7, encoding=None, delay=False, utc=False, atTime=None)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        return fh

    def __consoleHandler(self):
        formatter = ColoredFormatter(
            fmt=CONSOLE_FORMAT,
            datefmt="%a%d %H:%M",
            reset=True,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        )
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        return ch

    def __redisHandler(self, redis_client=None):
            if redis_client is None:
                self.redis_client = j.core.db

    def get(self, name=None, enable_only_me=False):
        """
        Return a logger with the given name. Name will be prepend with 'j.' so
        every logger return by this function is a child of the jumpscale root logger 'j'

        Usage:
            self.logger = j.logger.get(__name__)
        in library module always pass __name__ as argument.
        """
        if not name:
            path, ln, name, info = logging.root.findCaller()
            if path.startswith(j.dirs.libDir):
                path = path.lstrip(j.dirs.libDir)
                name = path.replace(os.sep, '.')
        if not name.startswith(self.root_logger_name):
            name = "%s.%s" % (self.root_logger_name, name)
        logger = logging.getLogger(name)
        if enable_only_me:
            logger.enable_only_me()
        return logger

    def setLevel(self, level):
        """
        Set logging level of the root logger
        This will affect all the childs loggers. A too verbose logging level
        on root logger can reduce readibility
        """
        self._logger.setLevel(level)

    def log(self, msg=None, level=None, category=None):
        self._logger.log(level, msg)


class JSLogger(logging.Logger):

    def __init__(self, name):
        super(JSLogger, self).__init__(name)
        self.custom_filters = {}
        self.__only_me = False

    def enable_only_me(self):
        """
        Enable filtering. Output only log from this logger and its children.
        Logs from other modules are masked
        """
        if not self.__only_me and 'console' in j.logger.handlers:
            only_me_filter = logging.Filter(self.name)
            j.logger.handlers['console'].addFilter(only_me_filter)
            self.custom_filters["only_me"] = only_me_filter
            self.__only_me = True

    def disable_only_me(self):
        """
        Disable filtering on only this logger
        """
        import ipdb; ipdb.set_trace()
        if self.__only_me and 'console' in j.logger.handlers:
            j.logger.handlers['console'].removeFilter(self.custom_filters['only_me'])
            self.__only_me = False
