from Monitor import Monitor


class RealityCapture(object):
    """
    RealityCapture schedules monitoring on remote nodes given the gid and nid
    """
    def __init__(self):
        self.__jslocation__ = "j.tools.realitycapture"

    def get(self, controller):
        """
        Get a new reality capture scheduler

        :param controller: AgentController client instance.
        :return: Scheduler
        """
        return Monitor(controller)
