from datetime import datetime

from tornado.escape import json_encode
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        token = self.request.headers.get('authorization')
        if not token:
            return None
        else:
            token = token.split()[1]
            now = datetime.utcnow()
            c = self.db.cursor()
            c.execute(
                'SELECT * FROM users WHERE id = ('
                    'SELECT user_id FROM tokens WHERE id = ? AND expired > ?'
                ')',
                (token, now))
            user = c.fetchone()
            if user:
                user = dict(zip(user.keys(), user))
            return user

    def write_error(self, status_code, **kwargs):
        result = {
            'code': status_code,
            'message': kwargs.get('message'),
            'errors': kwargs.get('errors', self._reason),
        }
        self.finish(json_encode(result))
