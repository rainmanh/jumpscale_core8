# AYS Introduction

> Note that parts of the **AtYourService** documentation is deprecated. It's still heavily being reviewed.

## What is AYS?

AYS is a self-healing application management framework for cloud infrastructure and is installed as part of a JumpScale installation.

It combines functions such as:

- **Package Management** like Ubuntu's `apt-get`
- **Service Management** like Ubuntu's `service`
- **Configuration Management** like [ansible](http://www.ansible.com)
- **Build Tool** like [ant](http://ant.apache.org)
- **Monitoring Tool**

## What is a service?

A service is an abstraction for almost anything:

- Simple package i.e `mongodb`
- Server cluster i.e `mongodb cluster`
- Datacenter infrastructure i.e `rack(s) or a cluster of machines`
- Buisness logic i.e `user` and `team`
- Abstraction for any number of other services

## One command to rule them all

We use only one command `ays` to control everything:

- Convert a blueprint to one or more AYS service instances by executing `ays blueprint`
- Configure all dependencies of a given service by executing `ays init` on the AYS repository of the service
- Install a service by executing `ays install`
- Start all services: `ays start`
- Stop all services: `ays stop`
- check `ays --help` for a complete list of available commands


## Next

Next you will want to learn about:

- [AYS Definitions](Definitions/Definitions.md)
- [Life Cycle of an AYS Service](Service-Lifecycle.md)
- [AYS Commands](Commands/commands.md)
- [AYS File Locations & Details](FileDetails/FilesDetails.md)
- [AYS File System](G8OS-FS.md)
- [AYS Examples](Examples/Home.md)

```toml
!!!
title = "ays_intro"
tags= ["ays"]
categories= ["ays"]
```
