import os
import random
import sys
import uuid

import libvirt
import sqlite3
from tornado import template
from tornado.options import options

UNICODE_ASCII_CHARACTER_SET = ('abcdefghijklmnopqrstuvwxyz'
                               'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                               '0123456789')


# https://github.com/omab/python-social-auth/blob/master/social/utils.py#L49-L51
def import_module(name):
    __import__(name)
    return sys.modules[name]


# https://github.com/omab/python-social-auth/blob/master/social/utils.py#L54-L57
def module_member(name):
    mod, member = name.rsplit('.', 1)
    module = import_module(mod)
    return getattr(module, member)


def get_db_connect():
    db = sqlite3.connect(options.db, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    return db


# From oauthlib.common
def generate_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
    """Generates a non-guessable OAuth token

    OAuth (1 and 2) does not specify the format of tokens except that they
    should be strings of random characters. Tokens should not be guessable
    and entropy when generating the random characters is important. Which is
    why SystemRandom is used instead of the default random.choice method.
    """
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))


def get_nodes_connections(count, config_path,
                          create=False, template_path=None,
                          open_connections=True):
    result = {}
    if create:
        assert os.path.exists(template_path),\
            'Template path must be exist for nodes configs creation.'
        loader = template.Loader(template_path)
        for n in range(count):
            xml = loader.load('node.template.xml').generate(
                cpu={
                    'mhz': random.randrange(3000, 6000),
                    'model': 'i686',
                },
                memory=8192000,
                network={
                    'name': 'private',
                    'uuid': str(uuid.uuid4()),
                    'ip': '192.168.0.1',
                    'netmask': '255.255.255.0'
                },
                dhcp={
                    'start': '192.168.0.128',
                    'end': '192.168.0.253'
                },
                pool={
                    'name': 'default',
                    'uuid': str(uuid.uuid4())
                }
            ).decode('utf-8')
            node_config_path = os.path.join(config_path, '{}.xml'.format(n))
            with open(node_config_path, 'w') as f:
                f.write(xml)
            result.update({n: 'test://{}'.format(node_config_path)})
    else:
        for n in range(count):
            node_config_path = os.path.join(config_path, '{}.xml'.format(n))
            assert os.path.exists(node_config_path), \
                'Node config {} is not exist.'.format(node_config_path)
            result.update({n: 'test://{}'.format(node_config_path)})

    if open_connections:
        result = {k: libvirt.open(v) for k, v in result.items()}
    return result
