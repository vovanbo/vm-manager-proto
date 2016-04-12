from tornado import gen
from tornado.escape import json_encode

import commands
from decorators import authenticated
from handlers.base import BaseHandler
from tasks import Task


class GuestHandler(BaseHandler):
    @authenticated
    @gen.coroutine
    def get(self, id=None):
        task = Task(commands.start, self.get_current_user(), self.application,
                    params={'id': id, 'tmp': self})
        yield self.application.queue.put(task)
        self.write(task.id)

    @authenticated
    @gen.coroutine
    def post(self, id=None):
        self.write(json_encode(id))
