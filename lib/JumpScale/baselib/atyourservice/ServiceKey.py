from JumpScale import j


class ServiceKey:
    def __init__(self):
        self.domain = None
        self.name = None
        self.instance = None
        self.version = None

    @property
    def role(self):
        return self.name.split('.', 1)[0]

    @classmethod
    def get(self, domain=None, name=None, role=None, instance=None, version=None):
        service_key = ServiceKey()

        service_key.domain = domain
        if role and not name:
            service_key.role = name
        service_key.name = name
        service_key.instance = instance
        service_key.version = version

        return service_key

    @classmethod
    def parse(cls, input):
        if j.data.types.string.check(input):
            return cls._parser_str(input)
        else:
            from Service import Service
            from ServiceRecipe import ServiceRecipe
            if isinstance(input, Service):
                return cls._parse_service(input)
            elif isinstance(input, ServiceRecipe):
                return cls._parse_recipe(input)
        j.atyourservice.logger.error("can't parse %s." % input)
        return None

    @property
    def short(self):
        self._normalize()
        return "%s__%s" % (self.name, self.instance)

    def __str__(self):
        return "%s__%s__%s" % (self.domain, self.name, self.instance)

    def __repr__(self):
        return str(self)

    def _normalize(self):
        if self.domain:
            self.domain = self.domain.lower()
        if self.name:
            self.name = self.name.lower()
        if self.instance:
            self.instance = self.instance.lower()
        return self

    @classmethod
    def _parser_str(cls, key):
        """
        @return (domain,name,version,instance,role)
        """
        service_key = cls()

        key = key.lower()
        if key.find('@') != -1:
            key, version = key.split('@', 2)
        else:
            version = '0.1'

        ss = key.split('__')
        if len(ss) != 3:
            raise j.exceptions.Input("Parsing key faild. wrong forrmat: %s" % key)

        service_key.domain = ss[0]
        service_key.name = ss[1]
        service_key.instance = ss[2]
        service_key.version = version

        return service_key

    @classmethod
    def _parse_service(cls, service):
        service_key = cls()

        service_key.domain = service.domain
        service_key.name = service.name
        service_key.instance = service.instance
        service_key.version = service.version

        return service_key

    @classmethod
    def _parse_recipe(cls, recipe):
        service_key = cls()

        service_key.domain = recipe.template.domain
        service_key.name = recipe.template.name
        service_key.instance = None
        service_key.version = recipe.template.version

        return service_key
