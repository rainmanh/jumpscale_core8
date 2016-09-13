from JumpScale import j

from Worker import Worker

import inspect


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
        curdir = j.sal.fs.getDirName(inspect.getsourcefile(self.__init__))

        self._workerPath = j.sal.fs.joinPaths(curdir, "Worker.py")

        self.tmux = j.sal.tmux.createPanes4x4("workers", "actions", False)

    @property
    def queue(self):
        if self._queue is None:
            self._queue = self.db._db.getQueue('workers')
        return self._queue

    def startWorkers(self, nrworkers=8):

        paneNames = [pane.name for pane in self.tmux.panes]
        paneNames.sort()
        for i in range(nrworkers):
            name = paneNames[i]
            pane = self.tmux.getPane(name)
            cmd = "python3 %s -q worker%s" % (self._workerPath, i)
            pane.execute(cmd)

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
        while job is not None:
            job.state = "abort"
            job = self.queue.get_nowait()

    def removeAllJobs(self):
        """
        will empty queue & remove all jobs
        """
        job = self.queue.get_nowait()
        while job is not None:
            self.db.delete(job.dbobj.key)
            job = self.queue.get_nowait()
