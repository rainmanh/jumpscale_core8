from JumpScale import j

def cb():
    from .CiscoSwitchManager import CiscoSwitchManager
    return CiscoSwitchManager()


j.sal._register('ciscoswitch', cb)
