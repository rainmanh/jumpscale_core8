# Dhcp_ihc
```
j.sal.dhcp_ihc
```
##This library enables the user to configure DHCP by doing the followig:
* Configure DHCP on a certain network(interface) by giving a range of IP addresses which will be issued to clients booting up on the given network interface.
```
j.sal.dhcp_ihc.configure(ipFrom, ipTo, interface)
```
* Start, stop and restart the DHCP server.
```
j.sal.dhcp_ihc.start()
j.sal.dhcp_ihc.stop()
j.sal.dhcp_ihc.restart()
```
