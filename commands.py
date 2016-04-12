import logging

import time


def start(**kwargs):
    logging.info('BEGIN commands.start')
    time.sleep(5)
    logging.info('END commands.start, %s', kwargs)
    return kwargs
