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
        task = Task(self.get_current_user(), commands.start,
                    params={'id': id, 'tmp': 123})
        yield self.application.queue.put(task)
        self.write(task.id)

    @authenticated
    @gen.coroutine
    def post(self, id=None):
        self.write(json_encode(id))
