import uuid
from datetime import datetime

from tornado import gen

from settings import TaskStatus


class Task(object):
    def __init__(self, user, command,
                 params=None, status=TaskStatus.QUEUED, created=None):
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

    def __repr__(self):
        return 'Task {0.id} created on {0.created} ' \
               '(user: {0.user_id}, status: {0.status}, command: {0.command}).'\
            .format(self)

    @property
    def is_started(self):
        return self.status == TaskStatus.IN_PROGRESS

    @property
    def is_finished(self):
        return self.status in (TaskStatus.DONE, TaskStatus.FAILED)

    @property
    def user_id(self):
        return self.user.get('id')

    def start(self):
        self.status = TaskStatus.IN_PROGRESS
        self.started = datetime.utcnow()

    def finish(self, success=True, result=None):
        self.result = result
        self.finished = datetime.utcnow()
        self.status = TaskStatus.DONE if success else TaskStatus.FAILED

    @gen.coroutine
    def run(self):
        try:
            result = yield self.command(**self.params)
            success = True
        except Exception:
            result = None
            success = False
        return result, success

