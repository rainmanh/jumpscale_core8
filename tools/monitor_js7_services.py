#!/usr/bin/env python
"""
Python wrapper script to connect a current G8 installation and monitor its js7 services
"""

from JumpScale import j
import os
import requests

# parameters that should be in a configuration file
machine_ip = '192.168.103.154'
machine_login = 'cloudscalers'
machine_password = 'Ru1ek03xE'
base_path = '/opt/code/github/gig-projects/env_du-conv-3/'
remote_tmp_dir_path = '/optvar/tmp/%s' % machine_login
nodes = ['du-conv-3-01']


def check_cmd_result(exit_code, cmd):
    """
    Check if a command exit code is zero if not, raise an exception

    @param exit_code: exit code returned by the command executor
    @type exit_code: int

    @param cmd: Command that was executed
    @type cmd: str
    """
    if exit_code:
        raise j.exceptions.RuntimeError('Failed to execute command %s' % cmd)


result = {}
node_status = {'domain': '', 'name': '', 'instance': '', 'priority': '', 'status': '', 'ports': []}
executor=j.tools.executor.getSSHBased(addr=machine_ip, port=22,login=machine_login,passwd=machine_password)
cuisine=j.tools.cuisine.get(executor)

create_tmp_dir_cmd = 'echo %s | sudo -S mkdir %s'
cmd = create_tmp_dir_cmd % (machine_password, remote_tmp_dir_path)
exit_code, output = cuisine.executor.execute(cmd, die=True, checkok=None, async=False, showout=True, combinestdr=False, timeout=0, env={})
check_cmd_result(exit_code, cmd)

create_tmp_dir_cmd = 'echo %s | sudo -S chown %s:%s %s'
cmd = create_tmp_dir_cmd % (machine_password, machine_login, machine_login, remote_tmp_dir_path)
exit_code, output = cuisine.executor.execute(cmd, die=True, checkok=None, async=False, showout=True, combinestdr=False, timeout=0, env={})
check_cmd_result(exit_code, cmd)


cmd = "cd %s;echo %s | sudo -S ays execute -tt node.ssh -tn %%s --cmd 'ays status'"
cmd = cmd % (base_path, machine_password)
cmd = cmd % (nodes[0])
exit_code, output = cuisine.executor.execute(cmd, die=True, checkok=None, async=False, showout=True, combinestdr=False, timeout=0, env={})
check_cmd_result(exit_code, cmd)

get_remote_nodes_script = """
from JumpScale import j
import os

base_path = '%s'
os.chdir(base_path)
print j.clients.openvcloud.get().getRemoteNodes()
""" % base_path

get_remote_nodes_script_file_name = 'get_remote_nodes_%s.py' % j.data.idgenerator.generateRandomInt(1,10000)

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


client =  j.clients.openvcloud.get()
client.getRemoteNodes()
