## Introduction
To build your own client, you must understand some of the internals of the AgentController8 and how you can send and
receive data to/from it. This document can be used as a guide to build your own client to execute commands.

##Pre Read
Please make sure you understand the [command syntax](Command-Syntax.md).


## Communication
All communication between the client and the agent-controller2 is done over redis. You send new commands to agent-controller by
pushing some-commands to a queue. You wait for the answer by waiting on another queue. ect...

### Sending commands to agent controller 2
all commands must be pushed to the `cmds_queue` queue. Just build the correct command structure as descriped in [command syntax](Command-Syntax.md)
serialized it to json, and push it to `cmds_queue`. You can immediately see the command got received by the agentcontroller in the agentcontrller logs.

The agent-controller will make sure to deliver the task to the right agent(s).

### Receiving response:
To wait for job results, the client must do a blocking pop from the `cmds_queue_<cmd-id>` queue. Once the agent controller receives a response from the agent
it will immediately push it to this queue releasing the client.

>Note that, since the client must do `POP` of the responses, another `POP` can get the client to wait forever. So you only do the second wait if you are expecting
more results to be sent (fanout=true)

The agent controller will also store the command results(s) in a `HSET` named `jobresult:<job-id>` where each `key` in the dict is the `gid:nid` compination
and the value is the job result. This is useful if you need to get the command results in a non-blocking manner. Also the values in the dict are stored forever and not
poped, so you can read the results of the command any time in the future.

### View command history:
All the received commands are also pushed to `joblog` queue. This one should only be used for tracking purposes only.
