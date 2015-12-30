from JumpScale import j


class RecurringItem():
    def __init__(self, service,name,period,last):
        self.service = service
        self.name = name
        self.period = period
        self.periodSec = j.data.time.getDeltaTime(self.period)
        self.last = last

    def __repr__(self):
        if self.last != 0:
            return str("|%-20s | %-10s | %-10s | %-30s|\n" % (self.name,self.period,self.last,j.data.time.epoch2HRDateTime(self.last)))
        else:
            return str("|%-20s | %-10s | %-10s | %-30s|\n" % (self.name,self.period,self.last,""))

    def check(self):
        now=j.data.time.getTimeEpoch()
        if self.last<now-self.periodSec:
            #need to execute
            #
            self.service._executeOnNode("execute",cmd=self.name)

    def __str__(self):
        return self.__repr__()


class Recurring():
    def __init__(self, service):

        self.service = service

        if self.service.path == "" or self.service.path is None:
            raise RuntimeError("path cannot be empty")

        self.path = j.sal.fs.joinPaths(self.service.path, "recurring.md")
        self.items={}
        self._read()

    def add(self, name, period, last=0):
        key = "%s_%s" % (name, period)
        self.items[key] = RecurringItem(self.service,name,period,last)

    def check(self):
        for key, obj in self.items.items():
            obj.check()

    def start(self):

        for item in self.service.template.hrd_template.prefix("recurring"):
            name = item.split(".")[1].lower()
            self.add(name, self.service.template.hrd_template.getStr(item).strip("\""))

        for item in self.service.hrd.prefix("recurring"):
            name = item.split(".")[1].lower()
            self.add(name, self.service.hrd.getStr(item).strip("\""))

        self.write()

    def stop(self):
        j.do.delete(self.path)

    def _read(self):
        pastHeader = False
        if j.sal.fs.exists(path=self.path):
            for item in j.sal.fs.fileGetContents(self.path).split("\n"):
                if not pastHeader:
                    if item.find('---') != -1:
                        pastHeader = True
                    continue

                if item.find("|") == 0 and item.find("||") != 0:
                    items = item.split("|")

                    last = int(items[3].strip())
                    name = items[1].strip()
                    period = items[2].strip()
                    self.add(name, period, last)
        else:
            self.items = {}

    def write(self):
        if self.items != {}:
            j.sal.fs.writeFile(filename=self.path, contents=str(self))

    def __repr__(self):
        out = "# recurring items\n\n"
        out += "|%-19s | %-9s | %-9s | %-29s|\n" % ("name", "period", "last", "last_human")
        out += "| ---  | --- | --- | --- |"
        for key, obj in self.items.items():
            out += "%s" % obj
        return out

    def __str__(self):
        return self.__repr__()
