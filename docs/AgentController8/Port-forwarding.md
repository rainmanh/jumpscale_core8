# Introduction

Agent comes integrated with `hubble` for port-forwarding and tunneling over `web socket`. And it works with no extra charges, or external dependencies.

# Configuration

```toml
[hubble]
controllers = []
```

The `hubble` section in the agent config file defines which controllers are allowed to forward 'hubble_tunnel_*' commands. An empty list means all controllers defined under the `controllers` section are allowed.

# How to use

Imagine a setup that looks like the following

- Controller
- Agent with gid=1, nid=1
- Agent with gid=1, nid=2

Fire a `js` shell and do the following:

```python
client = j.clients.agentcontroller.get(password='rooter')
client.tunnel_open(1, 1, 2222, '1.2', '127.0.0.1', 22)
```

This basically asks `agent 1.1` to open a tunnel that listens on it's local node on port `2222`, all received connections are gonna be tunneled to `agent 1.2` to `127.0.0.1:22` (which is `agent 1.2` localhost)

You can list all active tunnels on an agent by doing this

```python
tunnels = client.tunnel_list(1, 1)
print tunnels
[{u'gateway': u'1.2', u'ip': u'127.0.0.1', u'local': 2222, u'remote': 22}]
```

Or close it like this:

```python
client.tunnel_close(1, 1, 2222, '1.2', '127.0.0.1', 22)
```

> Tunnels can be only listed on the `opener` side. doing a client.tunnel_list(1, 2) will not return anything. Unless tunnels were opened on `agent 1.2`

> Hubble supports dynamic port allocation, if `local` were set to `0` it will pick a free port automatically for you. In this case, to close the opened tunnel the `tunnel_close` must take the actually opened port number.

```
!!!
title = "Port Forwarding"
date = "2017-04-08"
tags = []
```
