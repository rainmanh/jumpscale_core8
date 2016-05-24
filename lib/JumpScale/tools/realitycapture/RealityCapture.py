from Monitor import Monitor


class RealityCapture:
    """
    RealityCapture schedules monitoring on remote nodes given the gid and nid
    """
    def __init__(self):
        self.__jslocation__ = "j.tools.realitycapture"

    def get(self, controller, redis_address):
        """
        Get a new reality capture scheduler

        :param controller: AgentController client instance.
        :param redis_address: Address of the redis instances that the jumpscripts will use to report stats and logs

        :return: Scheduler
        """
        return Monitor(controller, redis_address)
