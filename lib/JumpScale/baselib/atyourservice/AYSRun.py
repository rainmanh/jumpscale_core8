from JumpScale import j
import traceback
import colored_traceback

from multiprocessing import Process, Queue

colored_traceback.add_hook(always=True)

import pygments.lexers
from pygments.formatters import get_formatter_by_name


class AYSRunStepAction(Process):
    """
    is what needs to be done for 1 specific action for a service
    """

    def __init__(self, runstep, service, model=None, result_q=None, error_q=None):
        super(AYSRunStepAction, self).__init__()
        self.name = runstep.action
        self.state = service.state.get(runstep.action, die=False)
        if self.state is None:
            self.state = "INIT"
        self.service = service
        self.runstep = runstep
        self.result = None
        self._model = model
        self._service_model = None
        self._service_hrd = None
        self._source = None
        self.logger = j.atyourservice.logger
        self.error_q = error_q
        self.result_q = result_q

    @property
    def model(self):
        if self._model is None:
            # print ("GET MODEL FROM ACTION")
            m = {}
            m["state"] = self.state
            m["key"] = self.service.key
            m["result"] = self.result
            if self.service.model is None:
                m["model"] = ""
            else:
                m["model"] = self.runstep.run.db.set_dedupe("model", j.data.serializer.json.dumps(self.service.model))
            m["hrd"] = self.runstep.run.db.set_dedupe("hrd", str(self.service.hrd))
            m["source"] = self.runstep.run.db.set_dedupe("source", self.service.getActionSource(self.runstep.action))
            self._model = m
        return self._model

    @property
    def service_model(self):
        if self._service_model is None:
            self._service_model = self.runstep.run.db.get_dedupe("model", self.model["model"]).decode()
            if self._service_model != "":
                self._service_model = j.data.serializer.json.loads(self._service_model)
        return self._service_model

    @property
    def service_hrd(self):
        if self._service_hrd is None:
            self._service_hrd = self.runstep.run.db.get_dedupe("hrd", self.model["hrd"]).decode()
        return self._service_hrd

    @property
    def source(self):
        if self._source is None:
            self._source = self.runstep.run.db.get_dedupe("source", self.model["source"]).decode()
        return self._source

    def _str_error(self, error):
        out = ''
        formatter = pygments.formatters.Terminal256Formatter(style=pygments.styles.get_style_by_name("vim"))

        if error.__str__() != "":
            out += "\n*TRACEBACK*********************************************************************************\n"
            # self.logger.error("\n*TRACEBACK*********************************************************************************\n")

            lexer = pygments.lexers.get_lexer_by_name("pytb", stripall=True)
            tb_colored = pygments.highlight(error.__str__(), lexer, formatter)
            print(tb_colored)
            out += tb_colored

        # self.logger.error("\n\n******************************************************************************************\n")
        out += "\n\n******************************************************************************************\n"
        return out

    def run(self):
        try:
            self.result = self.service.runAction(self.runstep.action)
            self.logger.debug('running stepaction: %s' % self.service)
            self.logger.debug('\tresult:%s' % self.result)
            self.result_q.put(self.result)
        except Exception as e:
            self.logger.debug('running stepaction with error: %s' % self.service)
            self.logger.debug('\tresult:%s' % self.result)
            self.logger.debug('\error:%s' % self._str_error(e))
            self.error_q.put(self._str_error(e))
            self.result_q.put(self.result)
            raise e

    def __repr__(self):
        out = "runstep action: %s!%s (%s)\n" % (self.service.key, self.name, self.state)
        if self.service_model != "":
            out += "model:\n%s\n\n" % j.data.text.indent(self.service_model)
        if self.service_hrd != "":
            out += "hrd:\n%s\n\n" % j.data.text.indent(self.service_hrd)
        if self.source != "":
            out += "source:\n%s\n\n" % j.data.text.indent(self.source)
        return out

    __str__ = __repr__


class AYSRunStep:

    def __init__(self, run, nr, action):
        """
        """
        self.run = run
        self.nr = nr
        self.actions = {}
        self.action = action
        self.state = "INIT"

    def addService(self, aysi, model=None):
        if aysi.key not in self.actions:
            self.actions[aysi.key] = AYSRunStepAction(self, aysi, model=model, result_q=Queue(), error_q=Queue())
        return self.actions[aysi.key]

    def exists(self, aysi):
        return aysi.key in self.actions

    def execute(self):
        self.run.aysrepo.logger.debug('***************')
        self.run.aysrepo.logger.debug('\n\t'.join(list(self.actions.keys())))

        for stepaction in self.actions.values(): stepaction.start()
        for stepaction in self.actions.values(): stepaction.join()

        for stepaction in self.actions.values():
            if not stepaction.exitcode != 0:
                stepaction.result = stepaction.error_q.get()
                stepaction.state = "ERROR"
                self.state = "ERROR"
                self.run.state = "ERROR"
            else:
                stepaction.result = stepaction.result_q.get()
                stepaction.state = "OK"
                stepaction.service.reload()

    @property
    def model(self):
        services = []
        for key, stepaction in self.actions.items():
            services.append(stepaction.model)
        m = {}
        m["actions"] = services
        m["action"] = self.action
        m["nr"] = self.nr
        m["state"] = self.state
        return m

    def __repr__(self):
        out = "step:%s (%s)\n" % (self.nr, self.state)
        for key, stepaction in self.actions.items():
            service = stepaction.service
            out += "- %-50s ! %-15s %s \n" % (service, self.action, stepaction.state)
        return out

    __str__ = __repr__


class AYSRun:

    def __init__(self, aysrepo, id=0, simulate=False):
        """
        """
        self.aysrepo = aysrepo
        self.steps = []
        self.lastnr = 0
        self.id = id
        self.state = "INIT"
        self.timestamp = j.data.time.getTimeEpoch()
        # j.actions.setRunId("ays_run_%s"%self.id)
        self.db = aysrepo.db
        if simulate:
            self.id = 0
            return
        if self.db is not None:
            if id == 0:
                # if id==0 need to increment
                self.id = self.db.increment("run")
            else:
                # need to load from db
                self._load(id)

    def _load(self, id):
        if not self.db.exists("run", str(id)):
            return
        data = self.db.get("run", str(id))
        model = j.data.serializer.json.loads(data)
        self.id = int(model["id"])
        self.state = model["state"]
        for stepmodel in model["steps"]:
            step = AYSRunStep(self, stepmodel["nr"], stepmodel["action"])
            for actionmodel in stepmodel["actions"]:
                key = actionmodel["key"]
                aysi = self.aysrepo.getServiceFromKey(key)
                action = step.addService(aysi, model=actionmodel)
            self.steps.append(step)

    def list(self):
        runs = self.db.list('run_index')
        return {run_id: self.db.get('run_index', run_id) for run_id in runs}

    def getFile(self, ttype, hash):
        return self.db.get(ttype, hash)

    def delete(self):
        if self.db is not None:
            from IPython import embed
            print("DEBUG NOW delete run")
            embed()

    def exists(self, aysi, action):
        for step in self.steps:
            if step.action != action:
                continue
            if step.exists(aysi):
                return True
        return False

    def newStep(self, action):
        self.lastnr += 1
        step = AYSRunStep(self, self.lastnr, action)
        self.steps.append(step)
        return step

    # def sort(self):
    #     for step in self.steps:
    #         keys = []
    #         items = {}
    #         res = []
    #         for service in step.services:
    #             items[service.key] = service
    #             keys.append(service.key)
    #         keys.sort()
    #         for key in keys:
    #             res.append(items[key])
    #         step.services = res

    @property
    def services(self):
        res = []
        for step in self.steps:
            for service in step.services:
                res.append(service)
        return res

    @property
    def action_services(self):
        res = []
        for step in self.steps:
            for service in step.services:
                res.append((step.action, service))
        return res

    @property
    def error(self):
        out = "%s\n" % self
        out += "***ERROR***\n\n"
        for step in self.steps:
            if step.state == "ERROR":
                for key, action in step.actions.items():
                    if action.state == "ERROR":
                        out += "STEP:%s, ACTION:%s" % (step.nr, step.action)
                        out += self.db.get_dedupe("source", action.model["source"]).decode()
                        out += str(action.result or '')
        return out

    def reverse(self):
        i = len(self.steps)
        for step in self.steps:
            step.nr = i
            i -= 1
        self.steps.reverse()

    def save(self):
        if self.db is not None:
            # will remember in KVS
            self.db.set("run", str(self.id), j.data.serializer.json.dumps(self.model))
            self.db.set("run_index", str(self.id), "%s|%s" % (self.timestamp, self.state))

    def execute(self):
        # j.actions.setRunId("ays_run_%s"%self.id)
        for step in self.steps:
            step.execute()
            if self.state == "ERROR":
                # means there was error in this run, then we need to stop
                self.save()
                raise j.exceptions.RuntimeError(self.error)
        self.state = "OK"
        self.save()

    @property
    def model(self):
        steps = [item.model for item in self.steps]
        m = {}
        m["reponame"] = self.aysrepo.name
        m["id"] = self.id
        m["steps"] = steps
        m["time"] = self.timestamp
        m["state"] = self.state

        return m

    def __repr__(self):
        out = "RUN:%s %s\n" % (self.aysrepo.name, self.id)
        out += "-------\n"
        for step in self.steps:
            out += "## step:%s\n\n" % step.nr
            out += "%s\n" % step
        return out

    __str__ = __repr__
