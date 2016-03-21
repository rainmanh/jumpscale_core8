from JumpScale import j


class StateItem():
    def __init__(self, service,name,period=0,last=0):
        self.service = service
        self.name = name
        self.period = period
        self.periodSec = j.data.time.getDeltaTime(self.period)
        self.last = last
        self.state = "INIT" #INIT,ERROR,OK,DISABLED,DO  DO means: execute the action method as fast as you can, init means it has not been started yet ever 
        self._action = None #is key of action

    def __repr__(self):
        if self.last != 0:
            return str("|%-20s | %-10s | %-10s | %-30s|\n" % (self.name,self.period,j.data.time.epoch2HRDateTime(self.last)))
        else:
            return str("|%-20s | %-10s | %-10s | %-30s|\n" % (self.name,self.period,""))

    def check(self):
        if self.periodSec>0:
            now=j.data.time.getTimeEpoch()
            if self.last<now-self.periodSec:
                #need to execute
                self.service._executeOnNode("execute",cmd=self.name)

    @property
    def action(self):
        from IPython import embed
        print ("DEBUG NOW action get state item")
        embed()
        
    @property
    def model(self):
        from IPython import embed
        print ("DEBUG NOW model")
        embed()
        

    def __str__(self):
        return self.__repr__()


class ServiceState():
    def __init__(self, service):

        self.service = service

        if self.service.path == "" or self.service.path is None:
            raise RuntimeError("path cannot be empty")

        self.path = j.sal.fs.joinPaths(self.service.path, "state.md")
        self.items={}
        self._read()

    def addRecurring(self, name, period, last=0):
        key = "%s_%s" % (name, period)
        self.items[key] = StateItem(self.service,name,period,last)

    def check(self):
        for key, obj in self.items.items():
            obj.check()

    def _read(self):
        pastHeader = False
        if j.sal.fs.exists(path=self.path):

            for line in j.sal.fs.fileGetContents(self.path).split("\n"):
                if pastHeader and line.find("```") != -1:
                    break

                if not pastHeader and line.find("```") != -1:
                        pastHeader = True
                        continue
                out+="%s\n"%line



        else:
            self.items = {}


        for item in self.service.recipe.hrd.prefix("recurring"):
            name = item.split(".")[1].lower()
            self.add(name, self.service.recipe.hrd.getStr(item).strip("\""))

        for item in self.service.hrd.prefix("recurring"):
            name = item.split(".")[1].lower()
            self.add(name, self.service.hrd.getStr(item).strip("\""))


        self.write()


    def write(self):
        if self.items != {}:
            j.sal.fs.writeFile(filename=self.path, contents=str(self))

    def __repr__(self):
        out = "# recurring items\n\n"
        out += "|%-19s | %-9s | %-29s| %-9s |\n" % ("name", "period", "last","state")
        out += "| ---  | --- | --- | --- |"
        for key, obj in self.items.items():
            out += "%s" % obj
        return out

    def __str__(self):
        return self.__repr__()
