# dns python is not python3 compatible

from JumpScale import j

def cb():
   from .BindDNS import BindDNS
   return BindDNS()


j.sal._register('bind', cb)
