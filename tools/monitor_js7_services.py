#!/usr/bin/env python
"""
Python wrapper script to connect a current G8 installation and monitor its js7 services
"""

from JumpScale import j
import requests

# parameters that should be in a configuration file
machine_ip = '192.168.103.168'
machine_login = 'cloudscalers'
machine_password = '9TUh9n0jG'
base_path = '/opt/code/github/0-complexity/du-conv-3'
nodes = ['du-conv-3-01']

result = {}
node_status = {'domain': '', 'name': '', 'instance': '', 'priority': '', 'status': '', 'ports': []}
executor=j.tools.executor.getSSHBased(addr=machine_ip, port=22,login=machine_login,passwd=machine_password)
cuisine=j.tools.cuisine.get(executor)

cmd = "cd %s;echo %s | sudo -S ays execute -tt node.ssh -tn %%s --cmd 'ays status'"

cmd = cmd % (base_path, machine_password)
cmd = cmd % (nodes[0])
exit_code, output = cuisine.executor.execute(cmd, die=True, checkok=None, async=False, showout=True, combinestdr=False, timeout=0, env={})

def parse_services_output(data):
    """
    Parses the ays status command output and build a node status dictionary

    @param data: input data, result of ays status command
    @type data: str

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

    
