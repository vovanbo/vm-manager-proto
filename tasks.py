import inspect
import uuid
from datetime import datetime

from tornado import gen

from settings import TaskStatus


class Task(object):
    def __init__(self, command, user, app,
                 params=None, status=TaskStatus.CREATED, created=None):
        assert callable(command), 'Task command must be callable'
        self.command = command
        self.id = str(uuid.uuid4())
        self.user = user
        self.params = params
        self.result = None
        self.status = status
        self.created = created or datetime.utcnow()
        self.started = None
        self.finished = None
        self._app = app

        self._save_to_db()

    def __repr__(self):
        return 'Task {0.id} created on {0.created} ' \
               '({1}, user: {0.user_id}, ' \
               'status: {0.status.name}).'.format(self, self.command_as_string)

    @property
    def is_started(self):
        return self.status == TaskStatus.IN_PROGRESS

    @property
    def is_finished(self):
        return self.status in (TaskStatus.DONE, TaskStatus.FAILED)

    @property
    def db(self):
        return self._app.db

    @property
    def executor(self):
        return self._app.executor

    @property
    def user_id(self):
        return self.user.get('id')

    @property
    def command_as_string(self):
        module = inspect.getmodule(self.command).__name__
        cmd = self.command.__name__
        return '{}.{}'.format(module, cmd)

    @gen.coroutine
    def run(self):
        self.status = TaskStatus.IN_PROGRESS
        self.started = datetime.utcnow()
        self._save_to_db()
        try:
            self.result = yield self.executor.submit(self.command,
                                                     **self.params)
            self.status = TaskStatus.DONE
        except Exception:
            self.result = None
            self.status = TaskStatus.FAILED
        self.finished = datetime.utcnow()
        self._save_to_db()
        return self.result

    def _save_to_db(self):
        c = self.db.cursor()
        c.execute(
            'INSERT OR REPLACE INTO '
            'tasks (id, user_id, command, params, result, status, created, started, finished) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (self.id, self.user_id, self.command_as_string,
             repr(self.params), repr(self.result),
             self.status.value, self.created, self.started, self.finished)
        )
        self.db.commit()
