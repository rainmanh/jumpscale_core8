from JumpScale import j

def cb():
    from .PerfTestToolsFactory import PerfTestToolsFactory
    return PerfTestToolsFactory()


j.tools._register('perftesttools', cb)
