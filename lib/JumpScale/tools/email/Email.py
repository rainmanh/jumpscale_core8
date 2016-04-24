class Email:
    def __init__(self):
        self.__jslocation__ = "j.tools.email"

    def getLast(self, num=100):
        """
        Gets most recent `num` emails

        :return: list
        """
        raise NotImplementedError()

    def pop(self):
        """
        Pops oldest email from the queue.

        :return: Message
        """
        raise NotImplementedError()

    def send(self):
        raise NotImplementedError()