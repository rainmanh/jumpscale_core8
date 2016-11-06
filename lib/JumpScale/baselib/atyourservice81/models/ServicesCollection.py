from JumpScale import j
from JumpScale.baselib.atyourservice81.models.ServiceModel import ServiceModel

import capnp
from JumpScale.baselib.atyourservice81 import model_capnp as ModelCapnp


class ServicesCollection:
    """
    This class represent a collection of AYS Services contained in an AYS repository
    It's used to list/find/create new Instance of Service Model object
    """

    def __init__(self, repository):
        self.repository = repository
        self.capnp_schema = ModelCapnp.Service
        self.category = "Service"
        self.namespace_prefix = 'ays:{}'.format(repository.name)
        namespace = "%s:%s" % (self.namespace_prefix, self.category.lower())
        self._db = j.servers.kvs.getRedisStore(namespace, namespace, **j.atyourservice.config['redis'])
        # for now we do index same as database
        self._index = j.servers.kvs.getRedisStore(namespace, namespace, **j.atyourservice.config['redis'])

    def new(self):
        model = ServiceModel(
            aysrepo=self.repository,
            capnp_schema=ModelCapnp.Service,
            category=self.category,
            db=self._db,
            index=self._index,
            key='',
            new=True)
        return model

    def get(self, key):
        model = ServiceModel(
            aysrepo=self.repository,
            capnp_schema=ModelCapnp.Service,
            category=self.category,
            db=self._db,
            index=self._index,
            key=key,
            new=False)
        return model

    def _list_keys(self, name="", actor="", state="", parent="", producer="", returnIndex=False):
        """
        @param name can be the full name e.g. myappserver or a prefix but then use e.g. myapp.*
        @param actor can be the full name e.g. node.ssh or role e.g. node.* (but then need to use the .* extension, which will match roles)
        @param parent is in form $actorName!$instance
        @param producer is in form $actorName!$instance

        @param state:
            new
            installing
            ok
            error
            disabled
            changed

        """
        if name == "":
            name = ".*"
        if actor == "":
            actor = ".*"
        if state == "":
            state = ".*"

        if parent == "":
            parent = ".*"
        elif parent.find("!") == -1:
            raise j.exceptions.Input(message="parent needs to be in format: $actorName!$instance",
                                     level=1, source="", tags="", msgpub="")
        if producer == "":
            producer = ".*"
        elif producer.find("!") == -1:
            raise j.exceptions.Input(message="producer needs to be in format: $actorName!$instance",
                                     level=1, source="", tags="", msgpub="")
        regex = "%s:%s:%s:%s:%s" % (name, actor, state, parent, producer)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, name="", actor="", state="", parent="", producer=""):
        """
        @param name can be the full name e.g. myappserver or a prefix but then use e.g. myapp.*
        @param actor can be the full name e.g. node.ssh or role e.g. node.* (but then need to use the .* extension, which will match roles)
        @param parent is in form $actorName!$instance
        @param producer is in form $actorName!$instance

        @param state:
            new
            installing
            ok
            error
            disabled
            changed

        """
        res = []
        for key in self._list_keys(name, actor, state, producer=producer, parent=parent):
            res.append(self.get(key))
        return res

    def destroy(self):
        self._db.destroy()
        self._index.destroy()
