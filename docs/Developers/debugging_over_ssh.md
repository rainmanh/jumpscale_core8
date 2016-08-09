

## Debugging over SSH


### principle

- You develop your code files on your local machine (e.g. your local Linux or Mac OSX)
   - JumpScale is locally installed
   - Git repos are checked out locally
- You have 1 or more (typically Ubuntu 16.04) machines running in server mode with SSH enabled and your public SSH key enabled
   - On this sever you have the JumpScale installed in debug or in sandboxed mode
- The j.tools.develop... tools help you to keep the code up to date and to upgrade/manage your remote development machine
   - The sync tools in the development tools will sync your local changes while you are using your editor to develop
   - Over ssh you can test your program on the remote machine


### Step 1: Create connection

```python
j.tools.develop.init("ovh4:22")
```

Now all other commands can be used on j.tools.develop...


### Step 2: Sync a local code tree to a remote one

All changes will be monitored constantly and synced:

```python
j.tools.develop.syncCode(ask=False, monitor=False, rsyncdelete=False, reset=False)

Docstring:
sync all code to the remote destinations

@param reset=True, means we remove the destination first
@param ask=True means ask which repo's to sync (will get remembered in redis)

File:      ~/opt/jumpscale8/lib/JumpScale/tools/develop/DevelopTools.py
```

Example:

```python
j.tools.develop.syncCode(True,True,True)
#will ask which dirs to sync and than start the monitor, will remove changes at other side

DO NOT USE GIT ON REMOTE SITE, ONLY ON LOCAL ONE
```

### How to connect & debug a remote sandboxed js8


```shell
#define which nodes to init,
#format="localhost,ovh4,anode:2222,192.168.6.5:23"
#this will be remembered in local redis for further usage
j.tools.develop.init()
j.tools.develop.jumpscale8(rw=True, synclocalcode=True, resetstate=True, monitor=True)
```

at end of process you will see something like
```sh
login to machine & do
cd /optrw/jumpscale8;source env.sh;js
Make a selection please:
   1: /Users/kristofdespiegeleer1/opt/code/github/jumpscale/ays_build_main
   2: /Users/kristofdespiegeleer1/opt/code/github/jumpscale/ays_core_it
   3: /Users/kristofdespiegeleer1/opt/code/github/jumpscale/ays_demo
   4: /Users/kristofdespiegeleer1/opt/code/github/jumpscale/ays_jumpscale8
   5: /Users/kristofdespiegeleer1/opt/code/github/jumpscale/dockers
   6: /Users/kristofdespiegeleer1/opt/code/github/jumpscale/docs8
   7: /Users/kristofdespiegeleer1/opt/code/github/jumpscale/jumpscale_core8
   8: /Users/kristofdespiegeleer1/opt/code/github/jumpscale/myrepo
   9: /Users/kristofdespiegeleer1/opt/code/github/jumpscale/ovcdeploy_ays2
   10: /Users/kristofdespiegeleer1/opt/code/github/jumpscale/palmlab
   11: /Users/kristofdespiegeleer1/opt/code/github/jumpscale/play8

   Select Nr, use comma separation if more e.g. "1,4", * is all, 0 is None: 5,7
```
the selection made will be remembered when used in later sessions.


### How to force to sync the code

```shell
#sync all code to the remote destinations
#@param reset=True, means we remove the destination first
#@param ask=True means ask which repo's to sync (will get remembered in redis)
j.tools.develop.syncCode(reset=True,ask=False,monitor=False,rsyncdelete=False)
```

This will sync all chosen code to the debug node.


### how to start the monitor

The monitor is a very nice tool to allow remote debugging.

It will check local changes and then over ssh send it to the remote node when change happens locally.

This allows you to use a local editor even when the bandwidth is not good towards the node you want to debug upon.

```shell
j.tools.develop.monitorChanges(sync=True,reset=False)
```

Result something like:

```shell
In [1]: j.tools.debug.monitorChanges(sync=True,reset=False)
EXECUTE ovh4:22: mkdir -p /optrw/code/dockers

rsync  ...
...

monitor:/Users/kristofdespiegeleer1/opt/code/github/jumpscale/dockers
monitor:/Users/kristofdespiegeleer1/opt/code/github/jumpscale/jumpscale_core8
copy: /Users/kristofdespiegeleer1/opt/code/github/jumpscale/jumpscale_core8/lib/JumpScale/tools/debug/Debug.py debugnode:ovh4:/optrw/jumpscale8/lib/JumpScale/tools/debug/Debug.py
```

If for whatever reason the monitoring doesn't start, try with `reset=True`.

Whatever the tool has been initialized with will be remembered when used a second time.
