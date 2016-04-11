from tornado import gen
from tornado.escape import json_encode

from decorators import authenticated
from handlers.base import BaseHandler


class TaskHandler(BaseHandler):
    @authenticated
    @gen.coroutine
    def get(self, id=None):
        self.write(json_encode(id))
