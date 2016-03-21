
from JumpScale import j
import netaddr
import re

class CuisineNet():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    def netconfig(self,interface,ipaddr,cidr=24,gateway=None,dns="8.8.8.8",masquerading=False):
        raise RuntimeError("please implement using systemd") #@todo (*2*)

    def netconfig(self,interface):
        raise RuntimeError("please implement using systemd") #@todo (*2*)

    @property
    def nics(self):
        res=[]
        for item in self.get_info():
            if item["name"] not in ["lo"]:
                res.append(item["name"])
        return res

    @property
    def ips(self):
        res=[]
        for item in self.get_info():
            if item["name"] not in ["lo"]:
                for ip in item["ip"]:
                    if ip not in res:
                        res.append(ip)
        return res

    @property
    def defaultgw(self):
        return self.cuisine.core.run("ip r | grep 'default' | awk {'print $3'}")

    @defaultgw.setter
    def defaultgw(self,val):
        raise RuntimeError("not implemented")


    def findnodes(self,range=None,ips=[]):
        """
        @param range in format 192.168.0.0/24
        if range not specified then will take all ranges of local ip addresses (nics)
        find nodes which are active around
        """
        if range==None:
            res=self.cuisine.net.get_info()
            for item in res:
                cidr=item['cidr']
                
                name=item['name']
                if not name.startswith("docker") and name not in ["lo"]:
                    if len(item['ip'])>0:
                        ip=item['ip'][0]
                        ipn=netaddr.IPNetwork(ip+"/"+str(cidr))
                        range=str(ipn.network)+"/%s"%cidr
                        ips=self.findnodes(range,ips)
            return ips
        else:            
            try:
                out=self.cuisine.core.run("nmap %s -n -sP | grep report | awk '{print $5}'"%range,showout=False)
            except Exception as e:
                if str(e).find("command not found")!=-1:
                    self.cuisine.package.install("nmap")
                    out=self.cuisine.core.run("nmap %s -n -sP | grep report | awk '{print $5}'"%range,showout=False)
            for line in out.splitlines():
                ip=line.strip()
                if ip not in ips:                    
                    ips.append(ip)
            return ips

        

    def get_info(self,device=None):
        """
        returns network info like

        [{'cidr': 8, 'ip': ['127.0.0.1'], 'mac': '00:00:00:00:00:00', 'name': 'lo'},
         {'cidr': 24,
          'ip': ['192.168.0.105'],
          'mac': '80:ee:73:a9:19:05',
          'name': 'enp2s0'},
         {'cidr': 0, 'ip': [], 'mac': '80:ee:73:a9:19:06', 'name': 'enp3s0'},
         {'cidr': 16,
          'ip': ['172.17.0.1'],
          'mac': '02:42:97:63:e6:ba',
          'name': 'docker0'}]

        """

        IPBLOCKS = re.compile("(^|\n)(?P<block>\d+:.*?)(?=(\n\d+)|$)", re.S)
        IPMAC = re.compile("^\s+link/\w+\s+(?P<mac>(\w+:){5}\w{2})", re.M)
        IPIP = re.compile("^\s+inet\s(?P<ip>(\d+\.){3}\d+)/(?P<cidr>\d+)", re.M)
        IPNAME = re.compile("^\d+: (?P<name>.*?)(?=:)", re.M)

        def parseBlock(block):
            result = {'ip': [], 'cidr': [], 'mac': '', 'name': ''}
            for rec in (IPMAC, IPNAME):
                match = rec.search(block)
                if match:
                    result.update(match.groupdict())
            for mrec in (IPIP, ):
                for m in mrec.finditer(block):
                    for key, value in list(m.groupdict().items()):
                        result[key].append(value)
            if j.data.types.list.check(result['cidr']):
                if len(result['cidr'])==0:
                    result['cidr']=0                 
                else:   
                    result['cidr']=int(result['cidr'][0])        
            return result

        def getNetworkInfo():
            output =self.cuisine.core.run("ip a", showout=False)
            for m in IPBLOCKS.finditer(output):
                block = m.group('block')
                yield parseBlock(block)

        res=[]
        for nic in getNetworkInfo():
            # print (nic["name"])
            if nic["name"]==device:
                return nic
            res.append(nic)
        
        if device!=None:
            raise RuntimeError("could not find device")
        return res            

    def getNetObject(self,device):
        n=self.get_info(device)
        net=netaddr.IPNetwork(n["ip"][0]+"/"+str(n["cidr"]))
        return net.cidr

    def getNetRange(self,device,skipBegin=10,skipEnd=10):
        """
        return ($fromip,$topip) from range attached to device, skip the mentioned ip addresses
        """
        n=self.getNetObject(device)
        return(str(netaddr.IPAddress(n.first+skipBegin)),str(netaddr.IPAddress(n.last-skipEnd)))
