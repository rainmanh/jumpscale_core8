import logging
import os

# Initiate testsuite logger
logger = logging.getLogger('jumpscale8_testsuite')
if not os.path.exists('tests/logs/jumpscale.log'):
    os.makedirs('tests/logs')
handler = logging.FileHandler('tests/logs/jumpscale.log')
formatter = logging.Formatter('%(asctime)s [%(testid)s] [%(levelname)s] %(message)s',
                              '%d-%m-%Y %H:%M:%S %Z')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
