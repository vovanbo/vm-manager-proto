from tornado import gen
from tornado.escape import json_encode

from decorators import authenticated
from handlers.base import BaseHandler


class GuestHandler(BaseHandler):
    @authenticated
    @gen.coroutine
    def get(self, id=None):
        self.write(json_encode(id))

    @authenticated
    @gen.coroutine
    def post(self, id=None):
        self.write(json_encode(id))