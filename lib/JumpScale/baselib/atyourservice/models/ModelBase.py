from JumpScale import j


class ModelBase():

    def __init__(self, category, db=None, key=""):
        self.logger = j.atyourservice.logger
        self._category = category
        if db is None:
            db = j.atyourservice.db.getDB(category)
        self._db = db
        if key != "" and self._db.exists(key):
            # will get from db
            self.load(key=key)
        else:
            self.dbobj = self._capnp.new_message()
            self._post_init()

    def _post_init(self):
        pass

    def _pre_save(self):
        # needs to be implemented see e.g. ActorModel
        pass

    def _get_key(self):
        # return a unique key to be used in db (std the key but can be overriden)
        return self.dbobj.key

    def index(self, db):
        # put indexes in db as specified
        pass

    def load(self, key=""):
        """
        please do not use key when loading, will use predefined one, only relevant in init
        """
        if key == "":
            key = self._get_key()
        # self.logger.debug('load actor from db. key:%s' % key)
        buff = self._db.get(key)
        # builder to true so we can change the content of the model
        self.dbobj = self._capnp.from_bytes(buff, builder=True)

    def save(self):
        self._pre_save()
        key = self._get_key()
        buff = self.dbobj.to_bytes()
        self._db.set(key, buff)

    def __repr__(self):
        ddict = self.dbobj.to_dict()
        # ddict = sortedcontainers.SortedDict(ddict)
        return j.data.serializer.json.dumps(ddict, True, True)

    __str__ = __repr__
