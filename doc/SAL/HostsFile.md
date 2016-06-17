## HostsFile

Hostsfile is used to do different operations on your `/etc/hosts` file, witch can be configured to be in any other directory


### Accessing it

You can access fs by
```py
h= j.sal.hostsfile.get()
```

### How does `/etc/hosts` look like?

```python
In [25]: cat /etc/hosts
127.0.0.1	localhost
::1	localhost ip6-localhost ip6-loopback
fe00::0	ip6-localnet
ff00::0	ip6-mcastprefix
ff02::1	ip6-allnodes
ff02::2	ip6-allrouters
172.17.0.2	myjs8xenial
```

### How to use it?

1- Getting an instance of hostsfile manager

```python
h=j.sal.hostsfile.get()
In [23]: h
Out[23]: <HostFileFactory.HostFile at 0x7f7c9f4917b8>

In [24]: h.hostfilePath
Out[24]: '/etc/hosts'
```

Note that `hostfilePath` is a property, you can change the location of the source file if it's located elsewhere.

2- You can use its simple interface to add, remove, query and check if an IP exists

```python
# checking if an IP exists in /etc/hosts
In [36]: h.existsIP("127.0.0.1")
Out[36]: True

In [37]: h.existsIP("172.17.0.2")
Out[37]: True

In [38]: h.existsIP("172.17.0.3")
Out[38]: False

# adding
In [39]: h.set("127.0.0.3", "somewhere.net")
In [42]: cat /etc/hosts
127.0.0.1	localhost
::1	localhost ip6-localhost ip6-loopback
fe00::0	ip6-localnet
ff00::0	ip6-mcastprefix
ff02::1	ip6-allnodes
ff02::2	ip6-allrouters
172.17.0.2	myjs8xenial
127.0.0.3 somewhere.net

# removing
In [43]: h.remove("127.0.0.3")

In [44]: cat /etc/hosts
127.0.0.1	localhost
::1	localhost ip6-localhost ip6-loopback
fe00::0	ip6-localnet
ff00::0	ip6-mcastprefix
ff02::1	ip6-allnodes
ff02::2	ip6-allrouters
172.17.0.2	myjs8xenial

# Get names by IP
In [53]: h.getNames("127.0.0.1")
Out[53]: ['localhost']

In [54]: h.getNames("127.0.0.2")
Out[54]: []

In [55]: h.getNames("172.17.0.2")
Out[55]: ['myjs8xenial']

In [56]: h.getNames("::1")
Out[56]: ['localhost', 'ip6-localhost', 'ip6-loopback']
```