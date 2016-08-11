from JumpScale import j


class JobController:
    """
    JobController is the interface on top of Jobs
    Allow you to put jobs on execution queues, get informations about jobs
    """

    def __init__(self, debug=False):
        """
        @param debug: if debug is enabled, serialization is done using json
        instead of binary capnpn. So it's easier to inspect
        @type  debug: bool
        """
        super(JobController, self).__init__()
        self.debug = debug
        self.db = j.atyourservice.kvs.get('jobcontroller')
        self.hset_key = 'job'

    def get(self, job_guid):
        """
        @param hset_key: Key of the hset where the job is stored
        @type hset_key: string # unneeded?

        @param job_guid: uniq identifier of a job
        @type job_guid: string

        @return: Job object
        @rtype: dict
        """
        job = self.db.hget(self.hset_key, job_guid)
        return j.data.serializers.loads(job)

    def set(self, job_model):
        """
        @param job_model: all informations about the job
        @type job_model: dict

        @return: info use in the get method
        @rtype: tuple, (hset_key, job_guid)
        """
        # create job_guid
        # set guid in queue
        # set info in hset
        q = self.getQueue('workers')
        q.put(job_model['guid'])
        self.db.hset(self.hset_key, job_model['guid'], j.data.serializers.dumps(job_model))
        return True

    def getQueue(self, queue_name):
        return self.db.getQueue('workers')

    def list(self, queue_key):
        """
        @param queue_key: key of the queue you want to inspect
        @type queue_key: string

        @return: list of tuples composed of (hset_key, job_guid)
        @rtype: list
        """
        raise NotImplementedError

    def delete(self, hset_key, job_guid):
        """
        @param hset_key: Key of the hset where the job is stored
        @type hset_key: string

        @param job_guid: uniq identifier of a job
        @type job_guid: string

        @return: True if successfully removed, False otherwise
        @rtype: bool
        """
        pass

    def delete_all(self, hset_key):
        """
        @param hset_key: Key of the hset where the jobs are stored
        @type hset_key: string

        @return: True if successfully removed, False otherwise
        @rtype: bool
        """
        pass

    def execute_job(self, **job_model):
        """
        temporary method while worker is not implemented yet.

        @param job_model: all informations about the job
        @type job_model: dict
        """
        job_guid = job_model['actorFQDN'] + job_model['actionCodeGUID'] + str(j.data.time.epoch)
        job_model['guid'] = job_guid
        job_model = j.atyourservice.AYSModel.Job.new_message(**job_model)
        self.set(job_model.to_dict())

    def queue_pop(self, queue, timeout):
        """
        @param queue: name of queue to listen on
        @type queue: string

        @param timeout: timeout in seconds
        @type timeout: int
        """
        queue = self.db.getQueue('workers')
        guid = queue.get()
        return self.get(guid)
