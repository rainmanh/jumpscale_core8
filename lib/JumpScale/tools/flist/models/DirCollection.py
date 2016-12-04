from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class DirCollection(base):
    """
    It's used to list/find/create new Instance of Dir Model object
    """

    def find(self, name=""):
        """
        @param state
            new
            ok
            error
            disabled
        """
        from IPython import embed
        print("DEBUG NOW oo")
        embed()
        raise RuntimeError("stop debug here")
