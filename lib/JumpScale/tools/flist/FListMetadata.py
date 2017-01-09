class FListMetadata:
    def __init__(self):
        self.__jslocation__ = "j.tools.flist"

    def create(self, parent_path, name, mode=""):
        raise NotImplementedError

    def mkdir(self, parent_path, name, mode=""):
        raise NotImplementedError

    def delete(self, path):
        raise NotImplementedError

    def chmod(self, path, mode=""):
        raise NotImplementedError

    def move(self, old_path, new_parent_path, name):
        raise NotImplemented

    def get_fs(self, root_path="/"):
        raise NotImplemented
