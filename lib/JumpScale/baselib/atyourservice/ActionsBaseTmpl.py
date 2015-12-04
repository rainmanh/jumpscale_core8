from JumpScale import j
import JumpScale.sal.screen
import os
import signal
import inspect


class ActionsBaseTmpl(object):
    """
    actions which belong to template
    """

    def build(self, serviceObj):
        folders = serviceObj.installRecipe()

        for src, dest in folders:
            serviceObj.upload2AYSfs(dest)
