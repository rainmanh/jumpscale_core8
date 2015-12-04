from JumpScale import j

def cb():
    from .PerformanceTrace import PerformanceTraceFactory
    return PerformanceTraceFactory()


j.tools._register('performancetrace', cb)


