<!-- toc -->
## j.core.platformtype.myplatform.executor.cuisine.solutions.vrouter

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/solutions/CuisineVRouter.py
- Properties
    - cuisine

### Methods

    

#### accesspoint(*sid='internet', passphrase='helloworld'*) 

```
will look for free wireless interface which is not the def gw
this interface will be used to create an accesspoint

```

#### bridge() 

```
create bridge which has accesspoint interface in it (wireless)

```

#### check() 

#### dhcpServer(*interfaces*) 

```
will run dhctp server in tmux on interfaces specified
if not specified then will look for wireless interface which is used in accesspoint and
    use that one

```

#### dnsServer() 

#### firewall() 

#### hostap() 

#### prepare() 

#### proxy() 

#### runSolution() 

