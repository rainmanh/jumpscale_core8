
from JumpScale import j
import netaddr
import re

class CuisineNet():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    
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
        return self.cuisine.run("ip r | grep 'default' | awk {'print $3'}")

    @defaultgw.setter
    def defaultgw(self,val):
        raise RuntimeError("not implemented")

    def get_info(self):
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
            output =self.cuisine.run("ip a", showout=False)
            for m in IPBLOCKS.finditer(output):
                block = m.group('block')
                yield parseBlock(block)

        res=[]
        for nic in getNetworkInfo():
            res.append(nic)
        
        return res            
