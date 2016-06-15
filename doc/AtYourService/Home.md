## AYS Introduction

> Note: parts of `at your service` documentation is deprecated. It's still heavily under refactoring.

**AtYourService** is a self-healing application management framework for cloud infrastructure abd is by default installed with jumpscale

It combines functions from:
- Package manager like Ubuntu's ```apt-get```
- Service manager like Ubuntu's ```service```
- Configuration manager like [ansible](http://www.ansible.com)
- Build tool like [ant](http://ant.apache.org)
- Monitoring tool

**What is a service?**

A service, either local or remote, is an abstraction for almost anything:
- Simple package i.e ```mongodb```
- A server cluster i.e ```mongodb cluster```
- Data center infrastructure i.e ```Rack(s) or a cluster of machines```
- Abstraction for several other services

**One command to rule them all**

We use only one command ```ays``` to control everything:
- Configure a service its dependencies (run from *AYS repo*): ```ays init```
- Install service: ```ays install ```
- Start all services: ```ays start ```
- Stop all services: ```ays stop```

