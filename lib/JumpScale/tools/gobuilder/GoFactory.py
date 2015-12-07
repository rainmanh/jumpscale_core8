from JumpScale import j
from .GoBuilder import GoBuilder

class GoFactory(object):
    """Tool to build go project"""
    def __init__(self):
        super(GoFactory, self).__init__()

    def get(self):
        return GoBuilder()
