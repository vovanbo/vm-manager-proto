import logging

import time
from tornado import gen


@gen.coroutine
def start(**kwargs):
    logging.info('BEGIN commands.start')
    time.sleep(3)
    logging.info('END commands.start, %s', kwargs)
    return kwargs
