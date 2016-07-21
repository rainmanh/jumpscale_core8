#!/usr/bin/env python
"""
Python wrapper script to connect a current G8 installation and monitor its js7 services
"""

from JumpScale import j

# parameters that should be in a configuration file
machine_ip = '192.168.103.168'
machine_login = 'cloudscalers'
machine_password = '9TUh9n0jG'
base_path = '/opt/code/github/0-complexity/du-conv-3'
nodes = ['du-conv-3-01']
executor=j.tools.executor.getSSHBased(addr=machine_ip, port=22,login=machine_login,passwd=machine_password)
cuisine=j.tools.cuisine.get(executor)

cmd = "cd %s;echo %s | sudo -S ays execute -tt node.ssh -tn %%s --cmd 'ays status'"

cmd = cmd % (base_path, machine_password)
cmd = cmd % (nodes[0])
cuisine.executor.execute(cmd, die=True, checkok=None, async=False, showout=True, combinestdr=False, timeout=0, env={})
