class BaseKVMComponent:

    def __init__(self, controller):
        self.controller = controller

    @property
    def is_created(self):
        return True

    @property
    def is_started(self):
        return True

    def create(self):
        return NotImplemented

    def start(self):
        return NotImplemented

    def delete(self):
        return NotImplemented

    def stop(self):
        return NotImplemented

    def to_xml(self):
        raise NotImplementedError()

    @classmethod
    def from_xml(cls, controller, xml):
        raise NotImplementedError()

    @classmethod
    def get_by_name(cls, controller, name):
        raise NotImplementedError()
