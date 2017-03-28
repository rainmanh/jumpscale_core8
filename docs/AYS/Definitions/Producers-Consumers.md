# Producers & Consumers

Each service instance can consume a service delivered by a producer. A producer is another service instance delivering a service.

The consumption of another service is specified in the `schema.hrd` file of a actor template ore recipe, using the `consume` keyword.

As an example of consumption, see the following `schema.hrd` specification:

```yaml
sshkey = descr:'authorized sshkey' consume:sshkey:1:2 auto
```

This describes that the service consumes a minimum of `1` and a maximum of `2` sshkey instances, and that it should auto-create these instances if they don't already exist. Minimum and maximum tags are optional. As well as `auto`.

See the section about [HRD](../BeyondBasics/HRD.html) files for more details.


```toml
!!!
title = "AYS Producer Consumer"
tags= ["ays","def"]
date = "2017-03-02"
categories= ["ays_def"]
```
