from JumpScale import j


class HRDType():

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

    def validate(self, value):
        if self.typeclass.check(value) == False:
            raise ValueError("Value:%s is not correct for %s" % (value, self))

    def ask(self):
        # print ("ASKKKK:%s"%self)
        if self.description == "":
            descr = "Please provide value for %s, type:%s" % (self.name, self.typeclass.NAME.lower())
        else:
            descr = "%s, type:%s" % (self.description, self.typeclass.NAME.lower())

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
            if ttype in ["string", "float"]:
                result = j.tools.console.askString(question=descr, defaultparam=self.default, regex=self.regex, retry=self.retry, validate=self.typeclass.check)

            elif ttype == "list":
                print("specify a list: is comma separated items")
                result = j.tools.console.askString(question=descr, defaultparam=self.default, regex=self.regex, retry=self.retry)
                result = self.typeclass.fromString(result)

            elif ttype == "multiline":
                result = j.tools.console.askMultiline(question=descr)
                result = self.typeclass.fromString(result)

            elif ttype == "int":
                result = j.tools.console.askInteger(question=descr,  defaultValue=self.default, minValue=self.minValue,
                                                    maxValue=self.maxValue, retry=self.retry, validate=self.typeclass.check)
                result = self.typeclass.fromString(result)

            elif ttype == "bool":
                if descr != "":
                    print(descr)
                result = j.tools.console.askYesNo()
                if result:
                    result = True
                else:
                    result = False
            elif ttype == "multichoice":
                if self.multichoice == []:
                    j.events.inputerror_critical("When type is multichoice in ask, then multichoice needs to be specified as well.")
                result = j.tools.console.askChoiceMultiple(self.multichoice, descr=descr, sort=True)
            elif ttype == "singlechoice":
                if self.singlechoice == []:
                    j.events.inputerror_critical("When type is singlechoice in ask, then singlechoice needs to be specified as well.")
                result = j.tools.console.askChoice(self.singlechoice, descr=descr, sort=True)

            elif ttype == 'dict':
                print("format to define a dictionary is to per line enter key=value")
                result = j.tools.console.askMultiline(question=descr)
                result = self.typeclass.fromString(result)
            else:
                j.events.inputerror_critical("Input type:%s is invalid (only: bool,int,str,string,dropdown,list,dict,float)" % ttype)
        return result

    def __str__(self):
        # r="hrdtype:%s"%self.name
        return str(self.__dict__)

    __repr__ = __str__


class HRDSchema():

    def __init__(self, content=""):
        self.items = {}
        self.items_with_alias = {}
        self.content = content
        if content != "":
            self.process(content)

    def process(self, content):
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("#") or line == "":
                continue
            if line.find("=") == -1:
                raise ValueError("Hrd schema not properly formatted, should have =, see '%s'" % line)

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
                raise ValueError("Hrd schema not properly formatted, type can only be string when regex used, see '%s'" % line)

            if tags.tagExists("minval") or tags.tagExists("maxval"):
                if ttype == "str":
                    ttype = "int"
                if ttype not in ["int", "integer", "float"]:
                    raise ValueError("Hrd schema not properly formatted, when minval used type needs to be int or float, see '%s'" % line)

            hrdtype = HRDType()
            hrdtype.name = name

            hrdtype.typeclass = j.data.types.getTypeClass(ttype)

            if tags.labelExists("list"):
                hrdtype.list = True

            if tags.tagExists("default"):
                if hrdtype.list:
                    hrdtype.default = j.data.types.list.fromString(tags.tagGet("default"), hrdtype.typeclass)
                else:
                    hrdtype.default = hrdtype.typeclass.fromString(tags.tagGet("default"))
            else:
                hrdtype.default = hrdtype.typeclass.get_default()

            if tags.tagExists("descr"):
                hrdtype.description = tags.tagGet("descr")
                hrdtype.description = hrdtype.description.replace("__", " ")
                hrdtype.description = hrdtype.description.replace("\\n", "\n")

            if tags.tagExists("consume"):
                c=tags.tagGet("consume")
                for item in c.split(","):
                    item=item.strip().lower()
                    items=item.split(":")
                    if len(items)==2:
                        #min defined
                        hrdtype.consume_nr_min=items[1]
                    elif len(items)==3:
                        #also max defined
                        hrdtype.consume_nr_min=items[1]
                        hrdtype.consume_nr_max=items[2]
                    hrdtype.consume_link=items[0]

            if tags.tagExists("parent"):
                c=tags.tagGet("parent")
                hrdtype.consume_nr_min=1
                hrdtype.consume_nr_max=1
                hrdtype.consume_link=c
                hrdtype.parent=c
                
            if tags.tagExists("minval"):
                hrdtype.minVal = hrdtype.typeclass.fromString(tags.tagGet("minval"))

            if tags.tagExists("maxval"):
                hrdtype.maxVal = hrdtype.typeclass.fromString(tags.tagGet("maxval"))

            if tags.tagExists("multichoice"):
                hrdtype.multichoice = j.data.types.list.fromString(tags.tagGet("multichoice"), "str")

            if tags.tagExists("singlechoice"):
                hrdtype.singlechoice = j.data.types.list.fromString(tags.tagGet("singlechoice"), "str")

            if tags.tagExists("alias"):
                hrdtype.alias = j.data.types.list.fromString(tags.tagGet("alias"), "str")

            if line.find("@ask") != -1 or line.find("@ASK") != -1:
                hrdtype.doAsk = True

            self.items[name] = hrdtype
            self.items_with_alias[name] = hrdtype
            for alias in hrdtype.alias:
                self.items_with_alias[alias] = hrdtype

    def hrdGet(self, hrd=None, args={}):
        if hrd is None:
            hrd = j.data.hrd.get(content="", prefixWithName=False)
        for key, ttype in self.items.items():
            val = None
            if ttype.name in args:
                val = args[ttype.name]
            else:
                if not hrd.exists(ttype.name):
                    if ttype.doAsk is False:
                        if ttype.default == '' or ttype.default is None:
                            j.events.inputerror_critical('ask is set to false for key \'%s\' and default value is empty' % key, category='schema.getHRD', msgpub='ask is set to false for %s and default value is empty' % key)
                        val = ttype.default
                    else:
                        val = ttype.ask()
                else:
                    continue  # no need to further process, already exists in hrd
            if ttype.list:
                try:
                    val=j.data.types.list.fromString(val, ttype=ttype.typeclass)
                except Exception as e:
                    from IPython import embed
                    print(9933)
                    embed()                    
            else:

                if j.data.types.list.check(val) and len(val)==1:
                    val=val[0] #this to resolve some customer types or yaml inconsistencies, if only 1 member we can use as a non list

                if j.data.types.string.check(val):
                    while val[0] in [" ['"] or val[-1] in ["' ]"]:
                        val=val.strip()
                        val=val.strip("[]")
                        val=val.strip("'")

                try:
                    val=ttype.typeclass.fromString(val)
                except Exception as e:
                    from IPython import embed
                    print(9922)
                    embed()
                    
                if j.data.types.list.check(val) and len(val)==1:
                    val=val[0] #this to resolve some customer types or yaml inconsistencies, if only 1 member we can use as a non list
            hrd.set(ttype.name,val)
        return hrd

    def __repr__(self):
        return self.content.strip()

    __str__ = __repr__
