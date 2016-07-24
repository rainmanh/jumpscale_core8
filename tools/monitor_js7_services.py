#!/usr/bin/env python
"""
Python wrapper script to connect a current G8 installation and monitor its js7 services
"""

from JumpScale import j
import os
import re
import requests

class Config():
    """
    Configuration class
    """
    # parameters that should be in a configuration file
    machine_ip = '192.168.103.154'
    machine_login = 'cloudscalers'
    machine_password = 'Ru1ek03xE'
    base_path = '/opt/code/github/gig-projects/env_du-conv-3/'



class MonitoringService():
    """
    Monitoring service class
    """
    def __init__(self, config):
        """
        Initialize new instance with specific configurations

        @param config: Configuration object, contianing all the required configurations for the monitoring service
        @type config: obj
        """
        self._config = config
        self.result = {}
        self._executor=j.tools.executor.getSSHBased(addr=config.machine_ip, port=22,login=config.machine_login,passwd=config.machine_password)
        self._cuisine=j.tools.cuisine.get(self._executor)
        # set sudo mode
        self._cuisine.core.sudomode = True
        self._get_remote_nodes_script = """
        from JumpScale import j
        import os

        base_path = '%s'
        os.chdir(base_path)
        print(j.clients.openvcloud.get().getRemoteNodes())
        """ % config.base_path

# node_status = {'domain': '', 'name': '', 'instance': '', 'priority': '', 'status': '', 'ports': []}

    def get_remote_nodes(self):
        """
        Retreives a list of remote physical nodes on the environment

        @return: list of nodes
        """
        result = []
        output = self._cuisine.core.execute_jumpscript(self._get_remote_nodes_script)
        """
        output would be something like
        "WARNING: no system redis found (port 9999, needs to be installed as instance 'system').\n[jumpscale      :node.ssh       :du-conv-3-01, jumpscale      :node.ssh       :du-conv-3-02, jumpscale      :node.ssh       :du-conv-3-03, jumpscale      :node.ssh       :du-conv-3-04]"
        """
        # get rid of the warning part
        pattern = '^.*\[(?P<nodes>.*)\].*'
        match = re.match(pattern, output, re.DOTALL | re.MULTILINE)
        if match:
            for node in map(lambda x: x.split(':')[-1], match.groupdict().get('nodes', '').split(',')):
                result.append(node)
        return result


    def parse_services_output(self, data, node):
        """
        Parses the ays status command output and build a node status dictionary

        @param data: input data, result of ays status command
        @type data: str

        @param node: Node where the data belong to
        @type node: str

        Example input data is:
        WARNING: no system redis found (port 9999, needs to be installed as instance 'system').
    [192.168.103.167:21001] sudo: ays status
    [192.168.103.167:21001] out: DOMAIN          NAME                 Instance   Prio Status   Ports
    [192.168.103.167:21001] out: ======================================================================
    [192.168.103.167:21001] out:
    [192.168.103.167:21001] out: jumpscale       autossh              du-conv-3-01    1 RUNNING
    [192.168.103.167:21001] out: jumpscale       redis                system        1 RUNNING  9999
    [192.168.103.167:21001] out: jumpscale       autossh              http_proxy    1 RUNNING
    [192.168.103.167:21001] out: jumpscale       statsd-collector     main          5 RUNNING  8126
    [192.168.103.167:21001] out: jumpscale       nginx                main         50 RUNNING
    [192.168.103.167:21001] out: jumpscale       jsagent              main        100 RUNNING  4446
    [192.168.103.167:21001] out: openvcloud      vncproxy             main        100 RUNNING  8091
    [192.168.103.167:21001] out:

    **OK
        """
        # for some reason someone decided that this is the format of the output, I would really like to know that person!
        # form = '%(domain)-15s %(name)-20s %(instance)-10s %(prio)4s %(status)-8s %(ports)s'
        keys = ('domain', 'name', 'instance', 'prio', 'status', 'ports')
        result = []
        for line in data.split('\n'):
            # remote all the lines that are not part of the actual output
            parts = line.split('out:')
            if len(parts) > 1:
                output = parts[-1]
                # split the output on one or more spaces after striping it
                output = output.strip()
                output_parts = re.split('\s+', output)
                if len(output_parts) >= 5 and output_parts[0] != 'DOMAIN':
                    if len(output_parts) == 5:
                        output_parts.append('')
                    result.append(dict(zip(keys, output_parts)))

        self.result[node] = result

    def run(self):
        """
        Run the monitoring service and return the results
        """
        nodes = self.get_remote_nodes()
        ays_status_cmd = "cd %s;ays execute -tt node.ssh -tn %%s --cmd 'ays status'" % self._config.base_path
        for node in nodes:
            cmd = ays_status_cmd % node
            output = self._cuisine.core.run(cmd=cmd, die=True, debug=None, checkok=False, showout=True, profile=False, replaceArgs=True, check_is_ok=False)
            self.parse_services_output(data=output, node=node)


if __name__ == '__main__':
    MonitoringService(Config()).run()
