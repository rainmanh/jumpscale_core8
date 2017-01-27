import logging
import asyncio
try:
    import uvloop
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
except:
    loop = asyncio.get_event_loop()

from JumpScale import j
from JumpScale.baselib.atyourservice81.server.app import app as sanic_app


# configure asyncio logger
asyncio_logger = logging.getLogger('asyncio')
asyncio_logger.handlers = []
asyncio_logger.addHandler(j.logger.handlers.consoleHandler)
asyncio_logger.addHandler(j.logger.handlers.fileRotateHandler)
asyncio_logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    loop.set_debug(True)

    # load the app
    j.atyourservice
    # start server
    sanic_app.run(debug=True, host='0.0.0.0', port=5000, workers=1, loop=loop)
