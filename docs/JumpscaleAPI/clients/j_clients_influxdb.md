<!-- toc -->
## j.clients.influxdb

- /opt/jumpscale8/lib/JumpScale/clients/influxdb_/Influxdb2.py

### Methods

    

#### get(*host='localhost', port=8086, username='root', password='root', database, ssl, verify_ssl, timeout, use_udp, udp_port=4444*) 

#### getByInstance(*instancename*) 

#### postraw(*data, host='localhost', port=8086, username='root', password='root', database='main'*) 

```
format in is
'''
hdiops,machine=unit42,datacenter=gent,type=new avg=25,max=37 1434059627
temperature,machine=unit42,type=assembly external=25,internal=37 1434059627
'''

```

