from JumpScale import j

import os
import sys
import time
import traceback
import copy
# don't do logging, slows down


class Process():

    def __init__(self, name="", method=None, args={}):
        self.name = name
        self.method = method
        self.args = args
        self._result = ""
        self._state = "start"
        self.error = None
        self.result = None
        self.out = ""
        self.outpipe = None
        self.state = "init"

    def start(self):
        rpipe, wpipe = os.pipe()
        pid = os.fork()
        if pid == -1:
            raise RuntimeError("Failed to fork() in prepare_test_dir")

        if pid == 0:
            # Child -- do the copy, print log to pipe and exit
            try:
                os.close(rpipe)
                os.dup2(wpipe, sys.stdout.fileno())
                os.dup2(wpipe, sys.stderr.fileno())
                os.close(wpipe)
                # print("ARGS:%s" % args)
                res = self.method(**self.args)
            except Exception as e:
                eco = j.errorconditionhandler.processPythonExceptionObject(e)
                jsontext = eco.toJson()
                print("***ERROR***")
                # error = {}
                # error["tb"] = traceback.print_exc(30, sys.stderr)
                # error["error"] = str(e)
                # print(j.data.serializer.json.dumps(res))
                print(jsontext)
                print("***END***")
                sys.stdout.flush()
                sys.stderr.flush()
                sys.stdout.close()
                os._exit(1)
            finally:
                print("***RESULTS***")
                print(j.data.serializer.json.dumps(res))
                print("***END***")
                sys.stdout.flush()
                sys.stderr.flush()
                sys.stdout.close()
                os._exit(0)

            print("***PANIC***")
            print(res)
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(0)

        else:
            os.close(wpipe)
            self.outpipe = os.fdopen(rpipe)
            self.pid = pid
            self.state = "running"
            # print(self)

    def waitpid(self):
        # print("wait child pid")
        try:
            os.waitpid(self.pid, os.WNOHANG)
        except:
            pass

    def wait(self):
        """
        will return 0 if no error
        will return 1 if error

        results in self.result & self.error

        """
        if self.pid == None:
            return
        while True:
            res = self.process(waitInSecWhenNoData=0.1)
            if res in [2, 1]:
                self.waitpid()
                return res

    def process(self, waitInSecWhenNoData=0):
        """
        returns
            1= ok
            2= error
            5= no data, waiting for next time we call this
        """
        if self.pid == None:
            return
        while True:
            res = self.process1(waitInSecWhenNoData=waitInSecWhenNoData)
            if res in [2, 1, 5]:
                if res in [2, 1]:
                    self.waitpid()
                return res

    def process1(self, waitInSecWhenNoData=0):
        """
        processes 1 readline out of

        returns
            1= ok
            2= error
            5= no data
            0= need next round of process 1

        """
        out = self.outpipe.readline()
        out = out.rstrip()
        if out == "":
            # wait little bit when nothing returned, otherwise will not be empty
            if waitInSecWhenNoData > 0:
                print("WAIT")
                time.sleep(waitInSecWhenNoData)
            # print("nodata")
            return 5

        if self._state == "start" and out == "***RESULTS***":
            self._state = "result"
            self.state = "getresult"
            self._result = ""
            return 0
        if self._state == "result":
            if out == "***END***":
                self.result = j.data.serializer.json.loads(self._result)
                self.state = "ok"
                return 1
            else:
                self._result += out
                # go for next lines untill ***END***
                return self.process()

        if self._state == "start" and out == "***ERROR***":
            self._state = "error"
            self.state = "error"
            self._result = ""
            return 0
        if self._state == "error":
            if out == "***END***":
                error = j.data.serializer.json.loads(self._result)
                self.error = j.errorconditionhandler.getErrorConditionObject(error)
                return 2
            else:
                self._result += out
                # go for next lines untill ***END***
                return self.process()

        # print(self)
        self.out += "%s\n" % out
        return 0

    def __repr__(self):
        out = "name:%s\n (%s)" % (self.name, self.state)
        if self.result != None:
            out += "res:\n%s\n" % self.result
        if self.out != "":
            out += "out:\n%s\n" % self.out
        if self.error != None:
            print("**ERROR**")
            print(self.error.__str__)
        return out

    def close(self):
        self.waitpid()
        self.outpipe.close()
        self.pid = None
        if self.state != "ok":
            j.sal.process.kill(self.pid)

    __str__ = __repr__


class ProcessManagerFactory:

    def __init__(self):
        self.__jslocation__ = "j.core.processmanager"
        self._lastnr = 0
        self.processes = {}

    def startProcess(self, method, args={}, name="", autoclear=True, autowait=True):
        if name == "":
            name = "process_%s" % self._lastnr
            self._lastnr += 1
        if len(self.processes) > 100 and autoclear:
            self.clear()
        if len(self.processes) > 100:

            if autowait:
                if autoclear == False:
                    raise j.exceptions.Input(message="cannot wait if autoclear=False",
                                             level=1, source="", tags="", msgpub="")
                while True:
                    print("too many subprocesses, am waiting")
                    time.sleep(1)
                    self.clear()
                    time.sleep(1)
                    if len(self.processes) < 100:
                        break
            else:
                raise j.exceptions.Input(message="cannot launch more than 200 sub processes",
                                         level=1, source="", tags="", msgpub="")

        p = Process(name, method, args)
        p.start()
        self.processes[p.name] = p
        return p

    def clear(self, error=False):
        keys = [item for item in self.processes.keys()]
        print(len(keys))
        for key in keys:
            p = self.processes[key]
            p.process()
            if p.state == "ok":
                p.close()
                self.processes.pop(p.name)
            if p.state == "error" and error:
                p.close()
                self.processes.pop(p.name)

    def test(self):

        def amethod(x=None, till=1):
            counter = 0
            print("ID:%s" % x)
            while True:
                counter += 1
                print(counter)
                time.sleep(1)
                if counter == till:
                    # raise j.exceptions.Input(message="issue", level=1, source="", tags="", msgpub="")
                    return(x)

        r = {}
        nr = 10
        for i in range(nr):
            r[i] = self.startProcess(amethod, {"x": i, "till": 1})

        for i in range(nr):
            r[i].wait()

        def eco_errortest():
            try:
                raise RuntimeError("myerror")
            except Exception as e:
                eco = j.errorconditionhandler.processPythonExceptionObject(e)
                jsontext = eco.toJson()
                eco2 = j.errorconditionhandler.getErrorConditionObject(ddict=j.data.serializer.json.loads(jsontext))
            print(eco2)

        # eco_errortest()

        def anerror(x=None, till=1):
            print("a line")
            print("a line2")
            j.logger.log("testlog")
            raise RuntimeError("this is generic python error")

        p = self.startProcess(anerror, {"x": i, "till": 1})
        p.wait()

        # next should print the error & the log
        print(p)

    def perftest(self):

        # can run more than 1000 process per sec

        def amethod(x=None, till=1):
            return(x)

        r = {}
        nr = 5000
        start = time.time()
        print("START")
        for i in range(nr):
            r[i] = self.startProcess(amethod, {"x": i, "till": 1})

        for i in range(nr):
            r[i].wait()

        print(r[100])

        stop = time.time()
        print("nr of processes done per sec:%s" % int(nr / (stop - start)))
