from JumpScale import j

def cb():
    from .Influxdb2 import InfluxdbFactory
    return InfluxdbFactory()


j.clients._register('influxdb', cb)
