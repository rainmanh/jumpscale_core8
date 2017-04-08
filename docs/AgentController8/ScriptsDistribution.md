# Introduction

As per the [[Agent Configuration]] page, agent support extension. It already comes shipped with 2 extensions:

- One that can talk to a local [syncthing](https://syncthing.net/) to dynamically add shared folders. Exposed as the `sync` command
- The other extension is to execute legacy jumpscripts. Exposed as the `legacy` command.

@ys packages for both the agent and the agent controller already takes advantage of this by sharing 2 folders between the controller and all the agents. the `legacy` folder and `jumpscripts` folder. And they get setup during the installation.

- the `legacy` folder is used to distribute the legacy jumpscripts.
- the `jumpscripts` folder is used to distribute the new style jumpscripts.

This basically mean that to update the scripts on all the agents, you just need to change the scripts under the controller node and the update will be propagated to all agents.

To try this out:

```bash
ays install -n AgentController8
ays install -n AgentController8_client

ays install -n agent2

#then install the legacy scripts package
ays install -n legacy_js_core
```

To run the scripts, make sure you have the `AgentController8_client` installed

```bash
ays install -n AgentController8_client
```

then in a js shell do

```python
legacy = j.clients.ac.getLegacyClient()
legacy.executeJumpscript(...)
```

```
!!!
title = "ScriptsDistribution"
date = "2017-04-08"
tags = []
```
