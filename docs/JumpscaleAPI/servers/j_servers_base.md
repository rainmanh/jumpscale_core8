<!-- toc -->
## j.servers.base

- /opt/jumpscale8/lib/JumpScale/servers/serverbase/ServerBaseFactory.py

### Methods

#### getDaemon(*name='unknown', sslorg, ssluser, sslkeyvaluestor*) 

```
is the basis for every daemon we create which can be exposed over e.g. zmq or sockets or
    http

daemon=j.servers.base.getDaemon()

class MyCommands:
    def __init__(self,daemon):
        self.daemon=daemon

    #session always needs to be there
            def pingcmd(self,session=session):
                return "pong"

            def echo(self,msg="",session=session):
                return msg

daemon.addCMDsInterface(MyCommands,category="optional")  #pass as class not as object !!!
    chose category if only 1 then can leave ""

#now you need to pass this to a protocol server, its not usable by itself

```

#### getDaemonClientClass() 

```
example usage, see example for server at self.getDaemon (implement transport still)

DaemonClientClass=j.servers.base.getDaemonClientClass()

myClient(DaemonClientClass):
    def __init__(self,ipaddr="127.0.0.1",port=5651,org="myorg",user="root",passwd="1234",s
    sl=False,roles=[]):
        self.init(org=org,user=user,passwd=passwd,ssl=ssl,roles=roles)

    def _connect(self):
        #everwrite this method in implementation to init your connection to server (the
    transport layer)
        pass

    def _close(self):
        #close the connection (reset all required)
        pass

    def _sendMsg(self, cmd,data,sendformat="m",returnformat="m"):
        #overwrite this class in implementation to send & retrieve info from the server
    (implement the transport layer)
        #@return (resultcode,returnformat,result)
        #item 0=cmd, item 1=returnformat (str), item 2=args (dict)
        #resultcode
        #    0=ok
        #    1= not authenticated
        #    2= method not found
        #    2+ any other error
        pass
        #send message, retry if needed, retrieve message

client=myClient()
print client.echo("atest")

```

#### initSSL4Server(*organization, serveruser, sslkeyvaluestor*) 

