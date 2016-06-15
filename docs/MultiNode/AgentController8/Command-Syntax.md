# Example Command
Commands are delivered to the `Agent` from the `Agent Controller` over long polling. Agent keeps polling the AC for jobs. Jobs are delivers as `json` objects as following

```json
 {
    "id": "<job-id>",
    "gid": <grid-id>,
    "nid": <node-id>,
    "name": "<command>",
    "args": {
        ...
    },
    "data": "<data-string>",
    "role": "<optional role>",
    "fanout": true or false,
}
```

* id: Job ID. Chosen by the caller
* gid: Grid ID
* nid: Node ID
* args: Agent speicific RUN arguments (also called `runargs` in some parts of the documentation).
* data (optional): Data string, will be fed to the sub-process over `stdin`. So it actually can be anything including serialized json data.
* role: (mutual exclusive with `gid`) specifies agent role that must execute this job. If provided the first agent to satisfy this role will get the job. There is a special role `*` which means (any agent).
* fanout: Fanout only effective when a `role` is provided. Basically all agents that satisfy the given role will get the job.

> If `role=*` and `fanout=true` this basically means **ALL** agents.

# args
Arguments fine-tunes the process. The arguments are interpreted by the Agent itself to control the behavior of the sub-process, unlike `data` which is passed unprocessed to the sub-process itself. Also called `runargs` in some parts of the documentation.
Basic arguments support the following args:

* `max_time`: How long the sub-process can run, 0 for (forever) or long running process, value > 0 means kill the process of execution time takes more than `max_time`. If max time is set to -1 this instructs the agent to *remember* the job and will rerun it on agent start (useful with `recurring_period`).
* `max_restart`: max times the process will be restarted if failed, if max_restart = 0 then no restart. If the process lived for more than 5 min before it failes the counter will be reset.
* `domain`: domain of jumpscript (to do categorization)
* `name`: name of jumpscript or cmd to execute (will give all a name)
* `loglevels`: list of log levels to process
* `loglevels_db`: list of log levels to be processed by DB logger (overrides the logger defaults)
* `loglevels_ac`: list of log levels to be processed by AC logger (overrides the logger defaults)
* `recurring_period`: 0 or 100
    seconds between recurring execute this cmd
    0 is default means not recurring, so only once
* `stats_interval`: 120 means we overrule the default for this process and only monitor this porcess every 120 seconds.
* queue: If queue is set, the command will wait on a job queue for serial execution. In other words no 2 processes with the same queue name will get executed on the same agent at the same. time

## execution environment
When using command `execute` or any of the external extensions the agent defines a set of environment variables that
can be accessed by the child process:
* `AGENT_HOME`: `CWD` of the agent
* `AGENT_GID`: Gid of the agent
* `AGENT_NID`: Nid of the agent
* `AGENT_CONTROLLER_NAME`: Name of the agent controller that intiated this command (As defined in the agent config)
* `AGENT_CONTROLLER_URL`: Base url of the agent controller
* `AGENT_CONTROLLER_CLIENT_CERT`: Path to agent client certificates
* `AGENT_CONTROLLER_CLIENT_CERT_KEY`: Path to agent client certificates key

#Built in commands
* execute
* get_cpu_info
* get_disk_info
* get_mem_info
* get_nic_info
* get_os_info
* killall
* ping
* restart
* get_msgs
* del_msgs
