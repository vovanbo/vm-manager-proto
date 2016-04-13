import inspect
import uuid
from datetime import datetime

from tornado import gen

from settings import TaskStatus


class Task(object):
    def __init__(self, command, user, app,
                 id=None, params=None, status=TaskStatus.CREATED, created=None,
                 result=None, started=None, finished=None):
        assert callable(command), 'Task command must be callable'
        self.command = command
        self.id = id if id else str(uuid.uuid4())
        self.user = user
        self.params = params
        if isinstance(status, TaskStatus):
            self.status = status
        elif isinstance(status, str):
            self.status = TaskStatus(int(status))
        self.created = created or datetime.utcnow()
        self.result = result
        self.started = started
        self.finished = finished
        self._app = app

    def __repr__(self):
        return '<Task(id={self.id!r}, command={self.command_as_string}, ' \
               'created={self.created!r}, user={self.user_id}, ' \
               'status={self.status.name}>.'.format(self=self)

    @property
    def is_queued(self):
        return self.status == TaskStatus.QUEUED

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

    def _save_to_db(self):
        self.db.execute(
            'INSERT OR REPLACE INTO '
            'tasks (id, user_id, command, params, result, status, created, started, finished) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (self.id, self.user_id, self.command_as_string,
             repr(self.params), repr(self.result),
             self.status.value, self.created, self.started, self.finished)
        )
        self.db.commit()

    @gen.coroutine
    def add_to_queue(self):
        yield self._app.queue.put(self)
        self.status = TaskStatus.QUEUED
        self._save_to_db()

    @gen.coroutine
    def run(self):
        self.status = TaskStatus.IN_PROGRESS
        self.started = datetime.utcnow()
        self._save_to_db()
        try:
            self.result = yield self.executor.submit(self.command,
                                                     **self.params)
            self.status = TaskStatus.DONE
        except Exception as e:
            self.result = repr(e)
            self.status = TaskStatus.FAILED
        self.finished = datetime.utcnow()
        self._save_to_db()
        return self.result
