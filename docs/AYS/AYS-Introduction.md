## AYS Introduction

> Note that parts of the **AtYourService** documentation is deprecated. It's still heavily being reviewed.

### What is AYS?

AYS is a self-healing application management framework for cloud infrastructure and is installed as part of a JumpScale installation.

It combines functions such as:

- **Package Management** like Ubuntu's `apt-get`
- **Service Management** like Ubuntu's `service`
- **Configuration Management** like [ansible](http://www.ansible.com)
- **Build Tool** like [ant](http://ant.apache.org)
- **Monitoring Tool**


### What is a service?**

A service, either local or remote, is an abstraction for almost anything:

- Simple package i.e `mongodb`
- Server cluster i.e `mongodb cluster`
- Datacenter infrastructure i.e `rack(s) or a cluster of machines`
- Buisness logic i.e `user` and `team`
- Abstraction for any number of other services


### One command to rule them all

We use only one command `ays` to control everything:

- Configure all dependencies of a given service by executing `ays init` on the AYS repository of the service
- Install a service by executing `ays install`
- Start all services: `ays start`
- Stop all services: `ays stop`

### Next

Next you will want to learn about:

- [AYS Definitions](Definitions/0-Definitions.md)
- [Life Cycle of an AYS Service](Service-Lifecycle.md)
- [AYS File System](AYS-FS.md)
- [AYS Portal](AYS-Portal.md)
- [AYS Commands](Commands/commands.md)
- [AYS File Locations & Details](FileDetails/FileDetails.md)
- [Building an AYS Service](Building.md)
- [AYS Examples](Examples/Home.md)