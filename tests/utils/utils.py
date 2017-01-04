import logging
import unittest
import time
import os
from testconfig import config
from subprocess import Popen, PIPE

class BaseTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(BaseTest, self).__init__(*args, **kwargs)
        self.user = config['main']['user']
        self.password = config['main']['password']
        self.branch = config['main']['branch']

    def setUp(self):
        self._testID = self._testMethodName
        self._startTime = time.time()
        self._logger = logging.LoggerAdapter(logging.getLogger('jumpscale8_testsuite'),
                                             {'testid': self.shortDescription() or self._testID})
        self.lg('Testcase %s Started at %s' % (self._testID, self._startTime))

    def tearDown(self):
        """
        Environment cleanup and logs collection.
        """
        if hasattr(self, '_startTime'):
            executionTime = time.time() - self._startTime
        self.lg('Testcase %s ExecutionTime is %s sec.' % (self._testID, executionTime))

    def lg(self, msg):
        self._logger.info(msg)

    def run_cmd_via_subprocess(self, cmd):
        sub = Popen([cmd], stdout=PIPE, stderr=PIPE, shell=True)
        out, err = sub.communicate()
        if sub.returncode == 0:
            return out.decode('utf-8')
        else:
            error_output = err.decode('utf-8')
            raise RuntimeError("Failed to execute command.\n\ncommand:\n{}\n\n".format(cmd, error_output))

    def check_package(self, package):
        try:
            self.run_cmd_via_subprocess('dpkg -l {}'.format(package))
            return True
        except RuntimeError:
            print("Dependant package {} is not installed".format(package))
            return False

    def execute_command_on_docker(self, dockername, cmd):
        return self.run_cmd_via_subprocess("docker exec {} /bin/sh -c '{}'".format(dockername, cmd))

    def convert_string_to_dict(self, string, split):
        str_list = string.split('\n')
        #remove empty strings found in a list
        str_list = filter(None, str_list)
        for i in str_list:
            var = "".join(i.split())
            str_list[str_list.index(i)] = var.split(':')
        return dict(str_list)
