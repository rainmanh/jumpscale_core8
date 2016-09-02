from JumpScale import j

ActionsBaseTmpl = j.atyourservice.getActionsBaseClassTmpl()


class ActionsTmpl(ActionsBaseTmpl):
    """
    implement methods of this class to change behavior of lifecycle management of service
    """
    # def init(self,serviceObj):
    #     """
    #     init function of the service object, always done on @ys central side
    #     """
    #     return True

    # def build(self,serviceObj):
    #     """
    #     build instructions for the service, make sure the builded service ends up in right directory, this means where otherwise binaries would run from
    #     """
    #     pass
