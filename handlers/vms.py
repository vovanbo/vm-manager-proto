from tornado import gen

from decorators import authenticated
from handlers.base import BaseHandler


class GuestsHandler(BaseHandler):
    @authenticated
    @gen.coroutine
    def get(self):
        self.write('Done!')
