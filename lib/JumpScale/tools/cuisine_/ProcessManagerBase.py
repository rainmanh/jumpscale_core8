
class ProcessManagerBase:

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    def get(self, pm = None):
        from ProcessManagerFactory import ProcessManagerFactory
        return ProcessManagerFactory.get(self.cuisine, pm)