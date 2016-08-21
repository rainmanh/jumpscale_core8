from JumpScale import j
import random


class HRDType:

    def __init__(self):
        self.name = ""
        self.typeclass = None
        self.list = False
        self.default = None
        self.description = ""
        self.regex = ""
        self.minVal = 0
        self.maxVal = 0
        self.multichoice = []
        self.singlechoice = []
        self.alias = ""
        self.doAsk = False
        self.retry = 5
        self.consume_link = ""  # link to other service I require, described with name of role
        self.consume_nr_min = 0  # min amount we require
        self.consume_nr_max = 100  # max amount we require
        self.parent = ""
        self.auto = False
        self.hrd_ttype = None

    def validate(self, value):
        if self.typeclass.check(value) == False:
            raise ValueError("Value:%s is not correct for %s" % (value, self))

    def ask(self):
        # print ("ASKKKK:%s"%self)
        if self.description == "":
            descr = "Please provide value for %s, type:%s" % (
                self.name, self.typeclass.NAME.lower())
        else:
            descr = "%s, type:%s" % (
                self.description, self.typeclass.NAME.lower())

        ttype = self.typeclass.NAME

        if self.list:
            print("specify a list: are comma separated items")
            result = j.tools.console.askString(question=descr)
            result = result.replace(",", "\n")
            result = [item.strip() for item in result.split("\n")]
            result2 = []
            for item in result:
                result2.append(self.typeclass.fromString(item))
            result = result2

        else:
            if ttype in ["string", "float"] or self.typeclass.BASETYPE == "string":
                result = j.tools.console.askString(
                    question=descr, defaultparam=self.default, regex=self.regex, retry=self.retry, validate=self.typeclass.check)

            elif ttype == "list":
                print("specify a list: is comma separated items")
                result = j.tools.console.askString(
                    question=descr, defaultparam=self.default, regex=self.regex, retry=self.retry)
                result = self.typeclass.fromString(result)

            elif ttype == "multiline":
                result = j.tools.console.askMultiline(question=descr)
                result = self.typeclass.fromString(result)

            elif ttype in ['int', 'integer']:
                result = j.tools.console.askInteger(question=descr, defaultValue=self.default, minValue=self.minVal,
                                                    maxValue=self.maxVal, retry=self.retry, validate=self.typeclass.check)
                result = self.typeclass.fromString(result)

            elif ttype == "boolean":
                if descr != "":
                    print(descr)
                result = j.tools.console.askYesNo()
                if result:
                    result = True
                else:
                    result = False
            elif ttype == "multichoice":
                if self.multichoice == []:
                    raise j.exceptions.Input(
                        "When type is multichoice in ask, then multichoice needs to be specified as well.")
                result = j.tools.console.askChoiceMultiple(
                    self.multichoice, descr=descr, sort=True)
            elif ttype == "singlechoice":
                if self.singlechoice == []:
                    raise j.exceptions.Input(
                        "When type is singlechoice in ask, then singlechoice needs to be specified as well.")
                result = j.tools.console.askChoice(
                    self.singlechoice, descr=descr, sort=True)

            elif ttype == 'dict':
                print("format to define a dictionary is to per line enter key=value")
                result = j.tools.console.askMultiline(question=descr)
                result = self.typeclass.fromString(result)
            else:
                raise j.exceptions.Input(
                    "Input type:%s is invalid (only: bool,int,str,string,dropdown,list,dict,float)" % ttype)
        return result

    def __str__(self):
        # r="hrdtype:%s"%self.name
        return str(self.__dict__)

    __repr__ = __str__


class HRDSchema:

    def __init__(self, path="", content=""):
        if path != None:
            content = j.sal.fs.fileGetContents(path)
        # if content=="":
            # raise j.exceptions.Input("Content needs to be provided if path is empty")
        self.path = path
        self.content = content
        self.items = {}
        self.items_with_alias = {}
        self.content = content
        self.fieldsforcapnp = {}
        if content != "":
            self.process(content)

    def _raiseError(self, msg):
        if self.path != "":
            print("ERROR in schema:%s" % self.path)
        else:
            print("ERROR in schema:\n%s" % self.content)
        raise j.exceptions.RuntimeError(msg)

    def process(self, content):
        import collections
        self.fieldsforcapnp = collections.OrderedDict()
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("#") or line == "":
                continue
            if line.find("=") == -1:
                raise ValueError(
                    "Hrd schema not properly formatted, should have =, see '%s'" % line)

            name, tagstr = line.split("=", 1)
            name = name.strip()
            tagstr = tagstr.lower()

            tags = j.data.tags.getObject(tagstr)

            if tags.tagExists("type"):
                ttype = tags.tagGet("type").strip().lower()
                if ttype == "string":
                    ttype = "str"
            else:
                ttype = "str"

            if tags.tagExists("regex"):
                regex = tags.tagGet("regex")
            else:
                regex = None

            if regex != None and ttype != "str":
                raise ValueError(
                    "Hrd schema not properly formatted, type can only be string when regex used, see '%s'" % line)

            if tags.tagExists("minval") or tags.tagExists("maxval"):
                if ttype == "str":
                    ttype = "int"
                if ttype not in ["int", "integer", "float"]:
                    raise ValueError(
                        "Hrd schema not properly formatted, when minval used type needs to be int or float, see '%s'" % line)

            hrdtype = HRDType()
            hrdtype.name = name
            hrdtype.hrd_ttype = ttype

            hrdtype.typeclass = j.data.types.getTypeClass(ttype)

            if tags.labelExists("list"):
                hrdtype.list = True

            if tags.tagExists("default"):
                if hrdtype.list:
                    hrdtype.default = j.data.types.list.fromString(
                        tags.tagGet("default"), hrdtype.typeclass)
                else:
                    hrdtype.default = hrdtype.typeclass.fromString(
                        tags.tagGet("default"))
            else:
                if hrdtype.list == True:
                    hrdtype.default = []
                else:
                    try:
                        hrdtype.default = hrdtype.typeclass.get_default()
                    except:
                        self._raiseError("issue in default from hrdtype")

            if tags.tagExists("descr"):
                hrdtype.description = tags.tagGet("descr")
                hrdtype.description = hrdtype.description.replace("__", " ")
                hrdtype.description = hrdtype.description.replace("\\n", "\n")

            if tags.tagExists("consume"):
                c = tags.tagGet("consume")
                for item in c.split(","):
                    item = item.strip().lower()
                    items = item.split(":")
                    if len(items) == 2:
                        # min defined
                        hrdtype.consume_nr_min = items[1]
                    elif len(items) == 3:
                        # also max defined
                        hrdtype.consume_nr_min = items[1]
                        hrdtype.consume_nr_max = items[2]
                    hrdtype.consume_link = items[0]

            if tags.tagExists("parent"):
                c = tags.tagGet("parent")
                hrdtype.consume_nr_min = 1
                hrdtype.consume_nr_max = 1
                hrdtype.consume_link = c
                hrdtype.parent = c

            if tags.labelExists("auto"):
                hrdtype.auto = True

            if tags.labelExists("auto"):
                hrdtype.auto = True

            if tags.tagExists("minval"):
                hrdtype.minVal = hrdtype.typeclass.fromString(
                    tags.tagGet("minval"))

            if tags.tagExists("maxval"):
                hrdtype.maxVal = hrdtype.typeclass.fromString(
                    tags.tagGet("maxval"))

            if tags.tagExists("multichoice"):
                hrdtype.multichoice = j.data.types.list.fromString(
                    tags.tagGet("multichoice"), "str")

            if tags.tagExists("singlechoice"):
                hrdtype.singlechoice = j.data.types.list.fromString(
                    tags.tagGet("singlechoice"), "str")

            if tags.tagExists("alias"):
                hrdtype.alias = j.data.types.list.fromString(
                    tags.tagGet("alias"), "str")

            if line.find("@ask") != -1 or line.find("@ASK") != -1:
                hrdtype.doAsk = True
            self.fieldsforcapnp[name] = hrdtype
            self.items[name] = hrdtype
            self.items_with_alias[name] = hrdtype
            for alias in hrdtype.alias:
                self.items_with_alias[alias] = hrdtype

    def _sanitize_key(self, key):
        """
        make sure the key of an HRD schema has a valid format for Capnp Schema
        e.g.:
            ssh.port becomes sshPort
        """
        separator = ['_', '.']
        for sep in separator:
            if key.find(sep) != -1:
                ss = key.split(sep)
                key = ss[0]
                for s in ss[1:]:
                    key += s.capitalize()
        return key

    @property
    def capnpSchema(self):
        """
        create schema for capnp for this hrd schema
        important
        - order is respected (cannot change the id's of capnp schema)
        - need to store a unique id in the hrd schema so we know that we need to reuse this
        """
        typesmap = {
            'str': 'Text',
            'multiline': 'Text',
            'int': 'UInt32',
            'integer': 'UInt32',
            'bool': 'Bool',
            'float': 'Float32',
        }
        fid = 0
        schema_id = j.data.idgenerator.generateCapnpID()
        serializeddata = ""

        for k, ttype in self.fieldsforcapnp.items():
            k = self._sanitize_key(k)

            if ttype.list is not True:
                serializeddata += "\t" + k + \
                    " @%d :%s;\n" % (fid, typesmap[ttype.hrd_ttype])
            else:
                serializeddata += "\t" + k + \
                    " @%d :List(%s);\n" % (fid, typesmap[ttype.hrd_ttype])
            fid += 1

        if self.path:
            actorname = j.sal.fs.getBaseName(j.sal.fs.getParent(self.path))
            serializeddata += "\t actor @%d :Text;\n" % (fid)

        template = """
@%s;
struct Schema {
%s
}
""" % (schema_id, serializeddata)
        return template

    def hrdGet(self, hrd=None, args={}, path=None):
        """
        populate hrd out of the schema
        """
        if hrd == None:
            hrd = j.data.hrd.get(content="", prefixWithName=False)
        for key, ttype in self.items.items():
            val = None
            if ttype.name in args:
                val = args[ttype.name]
            else:
                if not hrd.exists(ttype.name):
                    if ttype.doAsk == False:
                        val = ttype.default
                    else:
                        val = ttype.ask()
                else:
                    continue  # no need to further process, already exists in hrd
            if ttype.list:
                try:
                    val = j.data.types.list.fromString(
                        val, ttype=ttype.typeclass)
                    ttype.hrd_ttype = "list"
                except Exception as e:
                    msg = "Type '%s' check failed for LIST of values '%s'.\nError:%s" % (
                        ttype.typeclass.NAME, val, e)
                    self._raiseError(msg)
            else:

                if j.data.types.list.check(val) and len(val) == 1:
                    # this to resolve some customer types or yaml
                    # inconsistencies, if only 1 member we can use as a non
                    # list
                    val = val[0]
                    #if not val.endswith(","): val = val +","
                if j.data.types.string.check(val):
                    while len(val) > 0 and (val[0] in [" ['"] or val[-1] in ["' ]"]):
                        val = val.strip()
                        val = val.strip("[]")
                        val = val.strip("'")

                try:
                    val = ttype.typeclass.fromString(val)
                except Exception as e:
                    msg = "Type '%s' check failed for value '%s'.\nError:%s" % (
                        ttype.typeclass.NAME, val, e)
                    self._raiseError(msg)

                if j.data.types.list.check(val) and len(val) == 1:
                    # this to resolve some customer types or yaml
                    # inconsistencies, if only 1 member we can use as a non
                    # list
                    val = val[0]

            hrd.set(ttype.name, val, ttype=ttype.hrd_ttype)
            if path == None:
                hrd.path = path

        return hrd

    def parentSchemaItemGet(self):
        """
        checks if one of the items of the scheme represents a parent, if no return none, otherwise return the item
        """
        for key, schemaItem in self.items.items():
            if schemaItem.parent != "":
                return schemaItem
        return None

    def consumeSchemaItemsGet(self):
        """
        checks if one of the items of the scheme represents a parent, if no return [], otherwise return the items

        """
        result = []
        for key, schemaItem in self.items.items():
            if schemaItem.consume_link != "" and schemaItem.parent == "":
                result.append(schemaItem)
        return result

    def __repr__(self):
        return self.content.strip()

    __str__ = __repr__
