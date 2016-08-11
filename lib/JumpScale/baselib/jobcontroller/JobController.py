from JumpScale import j

from Worker import Worker


class JobController:
    """
    JobController is the interface on top of Jobs
    Allow you to put jobs on execution queues, get informations about jobs
    """

    def __init__(self):
        self.__jslocation__ = "j.core.jobcontroller"
        self.db = j.atyourservice.db.job
        self._init = False
        self._queue = None

        from IPython import embed
        print("DEBUG NOW sdsdsds")
        embed()
        raise RuntimeError("stop debug here")

    @property
    def queue(self):
        if self._queue == None:
            self._queue = self.db._db.getQueue('workers')
        return self._queue

    def startWorkers(self, nrworkers=8):
        from IPython import embed
        print("DEBUG NOW start workers")
        embed()
        raise RuntimeError("stop debug here")

    def executeJob(self, jobguid):
        """
        """
        self.queue.put(jobguid)

    def getJobFromQueue(self, timeout=20):
        """
        @param queue: name of queue to listen on
        @type queue: string

        @param timeout: timeout in seconds
        @type timeout: int
        """
        guid = self.queue.get(timeout=timeout)
        return self.db.get(guid)

    def abortAllJobs(self):
        """
        will empty queue & abort all jobs
        abort means jobs will stay in db but state will be set
        """
        job = self.queue.get_nowait()
        while job != None:
            job.state = "abort"
            job = self.queue.get_nowait()

    def removeAllJobs(self):
        """
        will empty queue & remove all jobs
        """
        job = self.queue.get_nowait()
        while job != None:
            self.db.delete(job.dbobj.key)
            job = self.queue.get_nowait()
