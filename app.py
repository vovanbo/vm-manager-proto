import logging
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, parse_config_file, define, \
    options
from tornado.queues import Queue
from tornado.web import Application as BaseApplication, authenticated, url

from handlers import auth, base, tasks, vms
from settings import BASE_DIR, UUID_PATTERN, TaskStatus
from utils import get_nodes_connections

define('port', default=9443)
define('config_file', default='app.conf')
define('db', type=str, default=os.path.join(BASE_DIR, 'db', 'db.sqlite'))
define('token_length', type=int, default=60)
define('token_expire_time', type=timedelta, default=timedelta(minutes=10))
define('threads', type=int, default=4)
define('concurrency', type=int, default=4)
define('initial_data_file', type=str,
       default=os.path.join(BASE_DIR, 'db', 'initial.sql'))

define('nodes', type=int, default=10, group='vm')
define('nodes_config_path', type=str, group='vm',
       default=os.path.join(BASE_DIR, 'vm', 'nodes'))
define('create_nodes', type=bool, default=False, group='vm')

define('debug', default=False, group='application')
define('cookie_secret', default='SOME_SECRET', group='application')


class DemoHandler(base.BaseHandler):
    @authenticated
    @gen.coroutine
    def get(self):
        self.render('app.html')


class Application(BaseApplication):
    def __init__(self, handlers=None, default_host='', transforms=None,
                 **settings):
        assert os.path.exists(options.initial_data_file), \
            'File with initial SQL data must be exists!'
        assert options.nodes > 0, 'Count of nodes must be at least 1.'
        self.db = sqlite3.connect(options.db,
                                  detect_types=sqlite3.PARSE_DECLTYPES)
        self.db.row_factory = sqlite3.Row
        with open(options.initial_data_file) as f:
            self.db.executescript(f.read())
        self.queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=options.threads)
        self.nodes = get_nodes_connections(options.nodes,
                                           options.nodes_config_path,
                                           options.create_nodes,
                                           settings.get('template_path'))
        if options.create_nodes:
            self.db.execute('DELETE FROM domains')

        super(Application, self).__init__(
            handlers=handlers, default_host=default_host,
            transforms=transforms, **settings)


@gen.coroutine
def start_queue(app):

    @gen.coroutine
    def worker():
        while True:
            task = yield app.queue.get()
            try:
                logging.info('Task received! %s', task)
                result = yield task.run()
                logging.info('Task %s! %s', task.status.name, result)
            finally:
                app.queue.task_done()

    for _ in range(options.concurrency):
        worker()
    yield app.queue.join()


def main():
    if os.path.exists(options.config_file):
        parse_config_file(options.config_file)
    parse_command_line()

    app = Application(
        [
            url(r'/?', DemoHandler),
            url(r'/token/?', auth.TokenHandler),
            url(r'/tasks/?', tasks.TaskHandler),
            url(r'/tasks/({uuid})/?'.format(uuid=UUID_PATTERN),
                tasks.TaskHandler),
            url(r'/domains/?', vms.DomainHandler),
            url(r'/domains/({uuid})/?'.format(uuid=UUID_PATTERN),
                vms.DomainHandler),
            url(r'/nodes/?', vms.NodeHandler),
            url(r'/nodes/([\d+])', vms.NodeHandler)
        ],
        template_path=os.path.join(BASE_DIR, 'templates'),
        static_path=os.path.join(BASE_DIR, 'static'),
        **options.group_dict('application')
    )
    app.listen(options.port)

    logging.info('Listening on http://localhost:%d' % options.port)

    IOLoop.current().add_callback(start_queue, app)
    IOLoop.current().start()

if __name__ == '__main__':
    main()