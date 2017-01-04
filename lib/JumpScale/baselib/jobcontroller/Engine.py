
from JumpScale import j

import asyncio
import selectors

class ServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        # message = data.decode()
        # print('Data received: {!r}'.format(message))
        # print('Send: {!r}'.format(message))
        print(len(data  ))
        data2=str(len(data))+"\n"
        data3=data2.encode()
        self.transport.write(data3)


        # print('Close the client socket')
        # self.transport.close()

class Engine:
    """
    is our main engine, runs all the jobs in subprocesses
    """

    def __init__(self):
        pass

    def startSubProcess(self, command, outMethod="print", errMethod="print", timeout=600,
                       buffersize=5000000, useShell=True, cwd=None, die=True,
                       captureOutput=True):
        """
        @outmethod gets a byte string as input, deal with it e.g. print
        same for errMethod
        resout&reserr are lists with output/error
        return rc, resout, reserr
        @param captureOutput, if that one == False then will not populate resout/reserr
        @param outMethod,errMethod if None then will print to out
        """

        # TODO: *2 check if this works on windows
        # TODO: *2 there is an ugly error when there is a timeout (on some systems seems to work though)

        if cwd != None:
            if useShell == False:
                raise j.exceptions.Input(message="when using cwd, useshell needs to be used",
                                         level=1, source="", tags="", msgpub="")
            if "cd %s;" % cwd not in command:
                command = "cd %s;%s" % (cwd, command)

        if useShell:
            if "set -e" not in command:
                command = "set -e;%s" % command

        # if not specified then print to stdout/err
        if outMethod == "print":
            outMethod = lambda x: print("STDOUT: %s" % x.decode("UTF-8").rstrip())
            # outMethod = lambda x: sys.stdout.buffer.write(x)  #DOESN't work, don't know why
        if errMethod == "print":
            # errMethod = lambda x: sys.stdout.buffer.write(x)
            errMethod = lambda x: print("STDERR: %s" % x.decode("UTF-8").rstrip())

        async def _read_stream(stream, cb, res):
            while True:
                line = await stream.readline()
                if res != None:
                    res.append(line)
                if line:
                    if cb != None:
                        cb(line)
                else:
                    break

        async def _stream_subprocess(cmd, stdout_cb, stderr_cb, timeout=1, buffersize=500000, captureOutput=True):

            process = await asyncio.create_subprocess_exec(*cmd,
                                                           stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                                                           limit=buffersize)

            if captureOutput:
                resout = []
                reserr = []
            else:
                resout = None
                reserr = None

            rc = 0

            done, pending = await asyncio.wait([
                _read_stream(process.stdout, stdout_cb, resout),
                _read_stream(process.stderr, stderr_cb, reserr)
            ], timeout=timeout, return_when=asyncio.ALL_COMPLETED)

            if pending != set():
                # timeout happened
                print("ERROR TIMEOUT happend")
                for task in pending:
                    task.cancel()
                process.kill()
                return 124, resout, reserr

            await process.wait()
            rc = process.returncode
            return rc, resout, reserr


        if useShell:
            cmds = ["bash", "-c", command]
        else:
            cmds = [command]

        process= _stream_subprocess(
            cmds,
            outMethod,
            errMethod,
            timeout=timeout,
            buffersize=buffersize,
            captureOutput=captureOutput
        )




        # TODO: *1 if I close this then later on there is problem, says loop is closed
        # # if loop.is_closed() == False:
        # print("STOP")
        # # executor.shutdown(wait=True)
        # loop.stop()
        # loop.run_forever()
        # loop.close()
        #
        # if len(reserr) > 0 and reserr[-1] == b"":
        #     reserr = reserr[:-1]
        # if len(resout) > 0 and resout[-1] == b"":
        #     resout = resout[:-1]
        #
        # if die and rc > 0:
        #     out = "\n".join([item.rstrip().decode("UTF-8") for item in resout])
        #     err = "\n".join([item.rstrip().decode("UTF-8") for item in reserr])
        #     if rc == 124:
        #         raise RuntimeError("\nOUT:\n%s\nSTDERR:\n%s\nERROR: Cannot execute (TIMEOUT):'%s'\nreturncode (%s)" %
        #                            (out, err, command, rc))
        #     else:
        #         raise RuntimeError("\nOUT:\n%s\nSTDERR:\n%s\nERROR: Cannot execute:'%s'\nreturncode (%s)" %
        #                            (out, err, command, rc))
        #
        # return rc, resout, reserr

    def start(self):
        print("start")
        loop = asyncio.get_event_loop()

        coro = loop.create_server(ServerProtocol, '127.0.0.1', 4444)
        server = loop.run_until_complete(coro)

        print('Serving on {}'.format(server.sockets[0].getsockname()))

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

        # executor = concurrent.futures.ThreadPoolExecutor(5)
        # loop.set_default_executor(executor)
        # loop.set_debug(True)

        # loop.run_until_complete(
        #     )
