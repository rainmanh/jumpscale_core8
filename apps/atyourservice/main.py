import click
import logging
from JumpScale import j
import asyncio

try:
    import jsonschema
except:
    j.do.execute("pip3 install jsonschema")
    import jsonschema

try:
    from JumpScale.baselib.atyourservice81.server.app import app as sanic_app
except:
    print("needs:\npip3 install sanic==0.3.0")
    j.do.execute("pip3 install sanic")
    from JumpScale.baselib.atyourservice81.server.app import app as sanic_app

print("to see api:http://localhost:5000/")

# configure asyncio logger
asyncio_logger = logging.getLogger('asyncio')
asyncio_logger.handlers = []
asyncio_logger.addHandler(j.logger.handlers.consoleHandler)
asyncio_logger.addHandler(j.logger.handlers.fileRotateHandler)
asyncio_logger.setLevel(logging.DEBUG)


@click.command()
@click.option('--host', '-h', default='127.0.0.1', help='listening address')
@click.option('--port', '-p', default=5000, help='listening port')
@click.option('--debug', default=False, is_flag=True, help='enable debug logging')
def main(host, port, debug=False):
    async def cleanup(sanic, loop):
        while True:
            sleep = 60
            runs = j.core.jobcontroller.db.runs.find()
            limit = int(j.data.time.getEpochAgo("-2h"))
            for run in runs:
                if run.dbobj.state in ['error', 'ok']:
                    j.core.jobcontroller.db.runs.delete(state=run.dbobj.state, repo=run.dbobj.repo, toEpoch=limit)
            jobs = j.core.jobcontroller.db.jobs.find()
            for job in jobs:
                if job is None:
                    continue

                elif job.state in ['error', 'ok']:
                    j.core.jobcontroller.db.jobs.delete(actor=job.dbobj.actorName, service=job.dbobj.serviceName,
                                                        action=job.dbobj.actionName, state=job.state,
                                                        serviceKey=job.dbobj.serviceKey, toEpoch=limit)
            await asyncio.sleep(sleep)

    # load the app
    async def init_ays(sanic, loop):
        if debug:
            loop.set_debug(True)
        j.atyourservice.debug = debug
        j.atyourservice._start(loop=loop)

    # start server
    sanic_app.run(debug=debug, host=host, port=port, workers=1, before_start=init_ays, after_start=cleanup)


if __name__ == '__main__':
    main()
