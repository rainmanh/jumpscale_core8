# Working with Docker using the Docker SAL

We will go through `j.sal.docker` to manage Docker related operations using JumpScale framework.

Below you'll see how to:
- [Check the available images](#get-images)
- [Create a Docker container](#create-container)
- [Check whether the container is running](#check-running)
- [Get info about a container](#get-info)
- [Get the names of all containers](#get-names)
- [Get the names of the running containers](#get-names2)
- [Get detailed information](#docker-ps)


<a id="get-images"></a>
Let's check what images we have on the system:

```ipython
In [14]: j.sal.docker.getImages()
Out[14]:
['<none>:<none>',
 'jamesnetherton/docker-atom-editor',
 'proof2',
 '<none>:<none>',
 'proof',
 '<none>:<none>',
 'alpine',
 'mongo',
 'redis',
 'js8xenial',
 'centos',
 'nginx',
 'tarekatest0',
 'tarekatest',
 'ubuntu:xenial',
 'gopyruby:0.2',
 'gopyruby:0.1',
 'ahmed/py35vim:v1',
 '<none>:<none>',
 'ubuntu',
 'mywily:v2',
 'ubuntu:trusty',
 'ubuntu:wily',
 '<none>:<none>',
 'hello-world']
```


<a id="create-container"></a>
So let's create a container based on the latest Ubuntu image:

```
In [1]: c1=j.sal.docker.create(name="mytest1", base="ubuntu", myinit=False, ssh=False)
```

Here we are creating a container named `mytest1` based on the latest `ubuntu` image.

**myinit** is a special entry command for the image but we're not using it here, and we don't want `ssh` as well.


<a id="check-running"></a>
Let's check if it's running:

```
In [4]: c1.isRunning()
[Thu08 13:42] - ...lib/JumpScale/sal/docker/Container.py:94   - INFO     - read info of container mytest1:2a232407dd8bf95b46947b2fc490c2110a575598b292e67477c691399662b502

Out[4]: True
```

<a id="get-info"></a>
Let's get more info on that container:

```
In [9]: c1.info
[Thu08 13:47] - ...lib/JumpScale/sal/docker/Container.py:94   - INFO     - read info of container mytest1:2a232407dd8bf95b46947b2fc490c2110a575598b292e67477c691399662b502
Out[9]:
{'AppArmorProfile': '',
 'Args': [],
 'Config': {'AttachStderr': True,
  'AttachStdin': False,
  'AttachStdout': True,
  'Cmd': ['/bin/bash'],
  'Domainname': '',
  'Entrypoint': None,
  'Env': [],
  'Hostname': '2a232407dd8b',
  'Image': 'ubuntu',
  'Labels': {},
  'OnBuild': None,
  'OpenStdin': False,
  'StdinOnce': False,
  'Tty': True,
  'User': 'root',
  'Volumes': None,
  'WorkingDir': ''},
 'Created': '2016-09-08T11:37:53.797893739Z',
 'Driver': 'aufs',
 'ExecIDs': None,
 'GraphDriver': {'Data': None, 'Name': 'aufs'},
 'HostConfig': {'AutoRemove': False,
  'Binds': [],
  'BlkioBps': 0,
  'BlkioDeviceReadBps': None,
  'BlkioDeviceReadIOps': None,
  'BlkioDeviceWriteBps': None,
  'BlkioDeviceWriteIOps': None,
  'BlkioIOps': 0,
  'BlkioWeight': 0,
  'BlkioWeightDevice': None,
  'CapAdd': None,
  'CapDrop': None,
  'Cgroup': '',
  'CgroupParent': '',
  'ConsoleSize': [0, 0],
  'ContainerIDFile': '',
  'CpuCount': 0,
  'CpuPercent': 0,
  'CpuPeriod': 0,
  'CpuQuota': 0,
  'CpuShares': 0,
  'CpusetCpus': '',
  'CpusetMems': '',
  'Devices': None,
  'DiskQuota': 0,
  'Dns': [],
  'DnsOptions': [],
  'DnsSearch': [],
  'ExtraHosts': None,
  'GroupAdd': None,
  'IpcMode': '',
  'Isolation': '',
  'KernelMemory': 0,
  'Links': None,
  'LogConfig': {'Config': {}, 'Type': 'json-file'},
  'Memory': 0,
  'MemoryReservation': 0,
  'MemorySwap': 0,
  'MemorySwappiness': -1,
  'NetworkMode': 'default',
  'OomKillDisable': False,
  'OomScoreAdj': 0,
  'PidMode': '',
  'PidsLimit': 0,
  'PortBindings': {},
  'Privileged': False,
  'PublishAllPorts': False,
  'ReadonlyRootfs': False,
  'RestartPolicy': {'MaximumRetryCount': 0, 'Name': ''},
  'SandboxSize': 0,
  'SecurityOpt': None,
  'ShmSize': 67108864,
  'StorageOpt': None,
  'UTSMode': '',
  'Ulimits': None,
  'UsernsMode': '',
  'VolumeDriver': '',
  'VolumesFrom': None},
 'HostnamePath': '/var/lib/docker/containers/2a232407dd8bf95b46947b2fc490c2110a575598b292e67477c691399662b502/hostname',
 'HostsPath': '/var/lib/docker/containers/2a232407dd8bf95b46947b2fc490c2110a575598b292e67477c691399662b502/hosts',
 'Id': '2a232407dd8bf95b46947b2fc490c2110a575598b292e67477c691399662b502',
 'Image': 'sha256:b72889fa879c08b224cc33d260c434ec6295b56c7677b5ff6213b5296df31aaf',
 'LogPath': '/var/lib/docker/containers/2a232407dd8bf95b46947b2fc490c2110a575598b292e67477c691399662b502/2a232407dd8bf95b46947b2fc490c2110a575598b292e67477c691399662b502-json.log',
 'MountLabel': '',
 'Mounts': [],
 'Name': '/mytest1',
 'NetworkSettings': {'Bridge': '',
  'EndpointID': 'f9e7c329394243276acfb38fd67e9b1ae9a1f7a91df401db80e1390ca9f74954',
  'Gateway': '172.17.0.1',
  'GlobalIPv6Address': '',
  'GlobalIPv6PrefixLen': 0,
  'HairpinMode': False,
  'IPAddress': '172.17.0.3',
  'IPPrefixLen': 16,
  'IPv6Gateway': '',
  'LinkLocalIPv6Address': '',
  'LinkLocalIPv6PrefixLen': 0,
  'MacAddress': '02:42:ac:11:00:03',
  'Networks': {'bridge': {'Aliases': None,
    'EndpointID': 'f9e7c329394243276acfb38fd67e9b1ae9a1f7a91df401db80e1390ca9f74954',
    'Gateway': '172.17.0.1',
    'GlobalIPv6Address': '',
    'GlobalIPv6PrefixLen': 0,
    'IPAMConfig': None,
    'IPAddress': '172.17.0.3',
    'IPPrefixLen': 16,
    'IPv6Gateway': '',
    'Links': None,
    'MacAddress': '02:42:ac:11:00:03',
    'NetworkID': 'c77924ae91018d979cf583053518c1af8cbda3c081431a815ed964bd4d72afa6'}},
  'Ports': {},
  'SandboxID': 'dc5ecc7586bb59d96a62c1c493d74247c3bff7a53b29021e6ceed9341f02db4b',
  'SandboxKey': '/var/run/docker/netns/dc5ecc7586bb',
  'SecondaryIPAddresses': None,
  'SecondaryIPv6Addresses': None},
 'Path': '/bin/bash',
 'ProcessLabel': '',
 'ResolvConfPath': '/var/lib/docker/containers/2a232407dd8bf95b46947b2fc490c2110a575598b292e67477c691399662b502/resolv.conf',
 'RestartCount': 0,
 'State': {'Dead': False,
  'Error': '',
  'ExitCode': 0,
  'FinishedAt': '0001-01-01T00:00:00Z',
  'OOMKilled': False,
  'Paused': False,
  'Pid': 11823,
  'Restarting': False,
  'Running': True,
  'StartedAt': '2016-09-08T11:37:54.046714876Z',
  'Status': 'running'}}
```


<a id="get-names"></a>
We can check for the container names:

```
In [7]: j.sal.docker.containerNames
Out[7]:
['js8playpriv2',
 'stoic_jepsen',
 'js8playpriv',
 'myjs8xenial4',
 'mytest1',
 'sleepy_cori',
 'high_joliot',
 'goofy_brown',
 'myjs8xenial5',
 'h4',
 'js8play',
 'mynode3',
 'myjs8',
 'node2',
 'serene_brattain',
 'goofy_wilson',
 'mad_lumiere',
 'gopyrubytest2',
 'furious_stonebraker',
 'dreamy_fermat',
 'insane_bardeen',
 'adoring_fermi',
 'gopyrubytest3',
 'grave_bhabha',
 'mytest',
 'small_yonath',
 'mygogshome2',
 'angry_jones',
 'myjs7',
 'mynode1',
 'myjs8xenial2',
 'cranky_kilby',
 'loving_mirzakhani',
 'pensive_easley',
 'tarekatest999',
 'goofy_ritchie',
 'h2',
 'h3',
 'jovial_engelbart',
 'grave_lamarr',
 'loving_wright',
 'myjs8xenial',
 'cocky_bhabha',
 'node1',
 'js7',
 'tarekatest9',
 'prickly_liskov',
 'h1',
 'goofy_poincare',
 'test35',
 'myjs8home',
 'berserk_noether',
 'cockpitly',
 'mygogshome',
 'insane_swanson',
 'high_bhabha',
 'tiny_swanson',
 'mygitlab1',
 'myjs8xenial3',
 'tarekatest8',
 'fervent_babbage',
 'py35home',
 'gopyrubytest1']
```


<a id="get-names2"></a>
Checking for the names of the running containers:

```
In [8]: j.sal.docker.containersRunning
Out[8]: [docker:mytest1, docker:mytest]
```


<a id="docker-ps"></a>
We can also get detailed information:

```
In [5]: j.sal.docker.ps()
Out[5]:

[{'Command': '/bin/bash',
  'Created': 1473334673,
  'HostConfig': {'NetworkMode': 'default'},
  'Id': '2a232407dd8bf95b46947b2fc490c2110a575598b292e67477c691399662b502',
  'Image': 'ubuntu',
  'ImageID': 'sha256:b72889fa879c08b224cc33d260c434ec6295b56c7677b5ff6213b5296df31aaf',
  'Labels': {},
  'Mounts': [],
  'Names': ['/mytest1'],
  'NetworkSettings': {'Networks': {'bridge': {'Aliases': None,
     'EndpointID': 'f9e7c329394243276acfb38fd67e9b1ae9a1f7a91df401db80e1390ca9f74954',
     'Gateway': '172.17.0.1',
     'GlobalIPv6Address': '',
     'GlobalIPv6PrefixLen': 0,
     'IPAMConfig': None,
     'IPAddress': '172.17.0.3',
     'IPPrefixLen': 16,
     'IPv6Gateway': '',
     'Links': None,
     'MacAddress': '02:42:ac:11:00:03',
     'NetworkID': ''}}},
  'Ports': [],
  'State': 'running',
  'Status': 'Up 4 minutes'},
 {'Command': '/bin/bash',
  'Created': 1473334646,
  'HostConfig': {'NetworkMode': 'default'},
  'Id': '88b48cb67d12961304f981fc73f1516af9ae9798efa8f64798dc53b3bc5f103c',
  'Image': 'ubuntu',
  'ImageID': 'sha256:b72889fa879c08b224cc33d260c434ec6295b56c7677b5ff6213b5296df31aaf',
  'Labels': {},
  'Mounts': [],
  'Names': ['/mytest'],
  'NetworkSettings': {'Networks': {'bridge': {'Aliases': None,
     'EndpointID': '14deea48ecf9b3166c6eb2254a47cb7b6fb55b6d78b87c8838dc1dec6a6c03c3',
     'Gateway': '172.17.0.1',
     'GlobalIPv6Address': '',
     'GlobalIPv6PrefixLen': 0,
     'IPAMConfig': None,
     'IPAddress': '172.17.0.2',
     'IPPrefixLen': 16,
     'IPv6Gateway': '',
     'Links': None,
     'MacAddress': '02:42:ac:11:00:02',
     'NetworkID': ''}}},
  'Ports': [],
  'State': 'running',
  'Status': 'Up 5 minutes'}]
```

Next you will want to check the walkthrough documentation on [Installing Caddy using Cuisine](../Cuisine/install_caddy_on_docker.md) which builds on this walkthrough.

```
!!!
title = "Docker"
date = "2017-04-08"
tags = []
```
