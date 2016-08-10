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
        self.db = j.atyourservice.kvs.get('main')

    def get(self, hset_key, job_guid):
        """
        @param hset_key: Key of the hset where the job is stored
        @type hset_key: string

        @param job_guid: uniq identifier of a job
        @type job_guid: string

        @return: Job object
        @rtype: dict
        """
        raise NotImplementedError

    def set(self, job_model):
        """
        @param job_model: all informations about the job
        @type job_model: dict

        @return: info use in the get method
        @rtype: tuple, (hset_key, job_guid)
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def execute_job(self, job_model):
        """
        temporary method while worker is not implemented yet.

        @param job_model: all informations about the job
        @type job_model: dict
        """
