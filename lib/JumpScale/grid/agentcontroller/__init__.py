from JumpScale import j

def cb():
    from .AgentControllerFactory import AgentControllerFactory
    return AgentControllerFactory()


j.clients._register('agentcontroller', cb)
