import click
import logging

from JumpScale import j
from JumpScale.baselib.atyourservice81.server.app import app as sanic_app


# configure asyncio logger
asyncio_logger = logging.getLogger('asyncio')
asyncio_logger.handlers = []
asyncio_logger.addHandler(j.logger.handlers.consoleHandler)
asyncio_logger.addHandler(j.logger.handlers.fileRotateHandler)
asyncio_logger.setLevel(logging.DEBUG)

@click.command()
@click.option('--host','-h',default='127.0.0.1', help='listening address')
@click.option('--port','-p',default=5000, help='listening port')
@click.option('--debug', default=False, is_flag=True, help='enable debug logging')
def main(host, port, debug=False):

    # load the app
    async def init_ays(sanic, loop):
        if debug:
            loop.set_debug(True)
        j.atyourservice.start(loop=loop)

    # start server
    sanic_app.run(debug=debug, host=host, port=port, workers=1, before_start=init_ays)

if __name__ == '__main__':
    main()
