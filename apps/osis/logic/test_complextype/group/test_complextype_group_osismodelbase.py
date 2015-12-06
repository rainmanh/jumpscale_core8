from JumpScale import j

class test_complextype_group_osismodelbase(j.code.classGetJSRootModelBase()):
    """
    group of users
    """
    def __init__(self):
        pass
        self._P_id=0
        self._P_name=""
        self._P_guid=""
        self._P__meta=list()
        self._P__meta=["osismodel","test_complextype","group",1] #@todo version not implemented now, just already foreseen

    @property
    def id(self):
        return self._P_id

    @id.setter
    def id(self, value):
        if not isinstance(value, int) and value is not None:
            if isinstance(value, str) and j.core.types.integer.checkString(value):
                value = j.core.types.integer.fromString(value)
            else:
                msg="property id input error, needs to be int, specfile: /opt/jumpscale8/apps/osis/logic/test_complextype/model.spec, name model: group, value was:" + str(value)
                raise TypeError(msg)

        self._P_id=value

    @id.deleter
    def id(self):
        del self._P_id

    @property
    def name(self):
        return self._P_name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) and value is not None:
            if isinstance(value, str) and j.core.types.string.checkString(value):
                value = j.core.types.string.fromString(value)
            else:
                msg="property name input error, needs to be str, specfile: /opt/jumpscale8/apps/osis/logic/test_complextype/model.spec, name model: group, value was:" + str(value)
                raise TypeError(msg)

        self._P_name=value

    @name.deleter
    def name(self):
        del self._P_name

    @property
    def guid(self):
        return self._P_guid

    @guid.setter
    def guid(self, value):
        if not isinstance(value, str) and value is not None:
            if isinstance(value, str) and j.core.types.string.checkString(value):
                value = j.core.types.string.fromString(value)
            else:
                msg="property guid input error, needs to be str, specfile: /opt/jumpscale8/apps/osis/logic/test_complextype/model.spec, name model: group, value was:" + str(value)
                raise TypeError(msg)

        self._P_guid=value

    @guid.deleter
    def guid(self):
        del self._P_guid

    @property
    def _meta(self):
        return self._P__meta

    @_meta.setter
    def _meta(self, value):
        if not isinstance(value, list) and value is not None:
            if isinstance(value, str) and j.core.types.list.checkString(value):
                value = j.core.types.list.fromString(value)
            else:
                msg="property _meta input error, needs to be list, specfile: /opt/jumpscale8/apps/osis/logic/test_complextype/model.spec, name model: group, value was:" + str(value)
                raise TypeError(msg)

        self._P__meta=value

    @_meta.deleter
    def _meta(self):
        del self._P__meta

