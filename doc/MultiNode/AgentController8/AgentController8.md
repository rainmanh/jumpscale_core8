## Agentcontroller 8

JumpScale Agentcontroller in Go

Functions of a Agent8
- is a process manager
- a remote command executor that gets it's jobs and tasks by polling from AC (Agent Controller 2).
- tcp portforwarder
- statistics aggregator & forwarder

Generic features
- uses SSL with client certificates for security
- out stdour/err of subprocesses is being parsed & forwarded to agentcontroller in controlled way

The Agent will also monitor the jobs, updating the AC with `stats` and `logs`. All according to specs. 

## To install AgentController:
* [Installation](Install.html)


### Architecture

![](https://docs.google.com/drawings/d/1qsOzbv2XbwChgsLVV8qCydmH0ki9QLkaB336kt7D1Cg/pub?w=960&h=720)

[edit](https://docs.google.com/drawings/d/1qsOzbv2XbwChgsLVV8qCydmH0ki9QLkaB336kt7D1Cg/edit)
