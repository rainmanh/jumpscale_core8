# Example configuration

```toml
[main]
gid = 1
nid = 10
max_jobs = 100
message_id_file = "./.mid"
history_file = "./.history"
roles = []

[controllers]
    [controllers.main]
    url = "http://localhost:8966"
        [controllers.main.security]
        # UNCOMMENT THE FOLLOWING LINES TO USE SSL
        #client_certificate = "/path/to/client-test.crt"
        #client_certificate_key = "/path/to/client-test.key"

        # defines an extra CA to trust (used in case of server self-signed certs)
        # should be empty string otherwise.

        #certificate_authority = "/path/to/server.crt"

[extensions]
    [extensions.do_something]
    binary = "python2.7"
    cwd = "./python"
    args = ["{domain}/{name}.py"]

[channel]
cmds = ["main"] # long polling from agent 'main'

[logging]
    [logging.db]
    type = "DB"
    log_dir = "./logs"
    levels = []  # empty for all

    [logging.ac]
    type = "AC"
    flush_int = 300 # seconds (5min)
    batch_size = 1000 # max batch size, force flush if reached this count.
    controllers = [] # to all agents
    levels = [2]

    [logging.console]
    type = "console"
    levels = [2, 4, 7, 8, 9]

[stats]
interval = 60 # seconds
controllers = []

[startup]
    [startup.intialize_something]
    name = "do_something"
        [startup.syncthing.args]
        domaine = 'test'
        name = 'startup'
        loglevels_db = '*'
```

# Breaking down the configuration
The agent configuration is split into sections each control the agent sub-components for fine tuning all the agent behavior.

## main
The main section accepts the following attributes
* `gid`: The Grid ID of this agent
* `nid`: The Node ID of this agent (must be unique per grid)
* `max_jobs`: The max number of parallel jobs
* `message_id_file`: Where to store the unique message id counter. Agent log messages are numbered with unique ID that is persisted across reboots and spans the log database files (4 bytes)
* `history_file`: Files where persisted tasks are kept, which are rerun on agent restart. A job will be persisted if its `max_time` is set to `-1`.
* `roles`: A list of agent roles. Jobs can be sent directly to an agent with it's gid/nid, or to the first ready agent that has a specific role.

## controllers
Define controllers
* `url`: The controller base URL
* `security`: Defines certificates to use with this controller as defined below.

### security
Configures agent security. Agent support the option of using a client certificate for its communication with the controller

* `client_certificate`: client certificate file
* `client_certificate_key`: client certificate key file
* `certificate_authority`: server certificate to trust (Only required in case `controller` is using a self signed certificate). In that case you have to tell the agent to trust this certificate.

## extensions
Agent support lots of built in commands (check the specifications). But you still can extend this list with custom `execute` commands.
### Example
```toml
[extensions.do_something]
    binary = "python2.7"
    cwd = "./python"
    args = ["{domain}/{name}.py"]
```
the cmd section accepts the following parameters:
* `binary`: name of the executable, must be in `$PATH`, or set with full path.
* `cwd`: Working directory of binary
* `args`: List with extra arguments to the `binary`. Also can use the {key} notation to replace with values from the `runargs`.
* `env`: Dict with env variables that will be accessible to the binary (and the script)

By adding this section, you tell the agent to interpret all `do_something` as `execute` command

Internally, agent can receive CMD
```json
{
    "id": "<job-id>",
    "gid": 1,
    "nid": 10,
    "name": "do_something",
    "args": {
        "name": "test.py"
        "domain": "test"
    }
}
```
That will be internally interpreted as

```json
{
    "id": "<job-id>",
    "gid": 1,
    "nid": 10,
    "name": "execute",
    "args": {
        "name": "python2.7",
        "args": ["test/test.py"],
        "working_dir": "./python"
    }
}
```

## channel
Channel configures the long polling routine. It supports only 1 attribute so far `Cmds` which tells the agent which `ACs` to poll jobs from. It reference the `controllers` by controller key. Empty list for ALL controllers.

### example
```toml
[channel]
cmds = ["main"] # long polling from agent 'main'
```
> Note that, an empty list `[]` means ALL agents.

## stats
Configure how often the buffered stats will be flushed to the AC
Monitoring happens for each external process every 2 seconds, the calculated values plus the statsd messages from the external script are buffered inside the statsd deamon. The values then aggregated and pushed to AC on `interval`

### example
```toml
[stats]
interval = 60 # seconds
controllers = []
```
> Note: `controllers` reference which agents to update with stats (by controller key). Empty for all controllers.

## logging
see [logging](LogLevels.md)

> Note: scripts doesn't have to explicitly output levels 1 and 2. All the porcess stdout that doesn't have an explicit level will be considered of level 1. Same for stderr.

Each logger section configures a logger. You can configure as many loggers as you want. The logger name in the logger section doesn't really matter.

Currently we have on 3 types of loggers:
* `console`: output the logs to the agent stdout.
* `DB`: stores the logs to sqlite db
* `AC`: caches the logs into batches and send it to AC when max cache size is reached or after a certain amount of time (which is sooner)

Each logger type accepts certain configuration attributes.

### Type "DB"
```toml
[logging.db]
type = "DB"
log_dir = "./logs"
levels = []  # empty for all
```
* `log_dir`: Where to store the sqlite db files
* `levels`: A list with `default` levels that should be stored in the DB if not specified by the `Cmd` itself. An empty list `[]` for ALL.

### Type "AC"
```toml
[logging.ac]
type = "AC"
flush_int = 300 # seconds (5min)
batch_size = 1000 # max batch size, force flush if reached this count.
controllers = [] # to all agents
levels = [2]
```
* `flush_int`: Flush logs to configured agents every this amount of seconds
* `batch_size`: Max batch size. Note that flushing the logs will occur if max batch size reached or the `flush_int` has passed, which comes first.
* `levels`: A list with `default` levels that should be stored in the DB if not specified by the `Cmd` itself. An empty list `[]` for ALL.
* `controllers`: References which controller to update with the logs, empty list `[]` for ALL. Or define which one using the controller keys (as defined under `controllers`)

> Note: `levels` can be overridden by the cmd args. So you can force certain levels to be stored in DB (or sent to AC)

## startup
Startup specify tasks that the agent must execute once on agent boot. For example
```toml
[startup]
    [startup.intialize_something]
    name = "do_something"
        [startup.intialize_something.args]
        domaine = 'test'
        name = 'startup'
        loglevels_db = '*'
```

Tells the agent to run a task with id `intialize_something`. This task cmd is `do_something` with the runargs `startup.intialize_something.args`
> The output of this task will be discarded and never reported to the AC since it was initialized by the agent itself, but you still
can query the task log using the job ID (`intialize_something` in this case).
