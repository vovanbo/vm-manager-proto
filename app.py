import logging
import os
import sqlite3
from datetime import timedelta

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, parse_config_file, define, \
    options
from tornado.web import Application as BaseApplication, authenticated, url

from handlers.base import BaseHandler
from handlers.tokens import TokenHandler
from settings import BASE_DIR

define('port', default=9443)
define('config_file', default='app.conf')
define('db', default='db.sqlite')
define('token_length', type=int, default=60)
define('token_expire_time', type=timedelta, default=timedelta(minutes=10))

define('debug', default=False, group='application')
define('cookie_secret', default='SOME_SECRET', group='application')


class DemoHandler(BaseHandler):
    @authenticated
    @gen.coroutine
    def get(self):
        self.render('app.html')


class Application(BaseApplication):
    def __init__(self, handlers=None, default_host="", transforms=None,
                 **settings):
        self.db = sqlite3.connect(options.db)
        self.db.row_factory = sqlite3.Row
        cursor = self.db.cursor()
        with open('initial.sql') as f:
            cursor.executescript(f.read())
        super(Application, self).__init__(
            handlers=handlers, default_host=default_host,
            transforms=transforms, **settings)


def main():
    parse_command_line()
    if os.path.exists(options.config_file):
        parse_config_file(options.config_file)

    app = Application(
        [
            url(r'/', DemoHandler),
            url(r'/token/', TokenHandler)
        ],
        template_path=os.path.join(BASE_DIR, 'templates'),
        static_path=os.path.join(BASE_DIR, 'static'),
        **options.group_dict('application')
    )
    app.listen(options.port)

    logging.info('Listening on http://localhost:%d' % options.port)
    IOLoop.current().start()

if __name__ == '__main__':
    main()