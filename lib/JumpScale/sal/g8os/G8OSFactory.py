from JumpScale.sal.g8os.Node import Node


class G8OSFactory(object):
    """Factory for G8OS SAL"""

    def __init__(self):
        self.__jslocation__ = "j.sal.g8os"

    def get_node(self, addr, port=6379, password=None):
        """
        Returns a Node object that represent a G8OS node reachable
        at addr:port
        """
        return Node(
            addr=addr,
            port=port,
            password=password,
        )
