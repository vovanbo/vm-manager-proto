import logging

import time

# WARNING: All of commands results must be JSON-serializable values or structs!


def start(**kwargs):
    logging.info('BEGIN commands.start')
    time.sleep(5)
    logging.info('END commands.start, %s', kwargs)
    return [{
        'id': kwargs.get('id')
    }, ]
