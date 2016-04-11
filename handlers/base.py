from datetime import datetime

from tornado.escape import json_decode
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    def get_current_user(self):
        token = self.request.headers.get('authorization')
        if not token:
            return None
        else:
            token = token.split()[1]
            now = datetime.utcnow()
            c = self.application.db.cursor()
            c.execute(
                'SELECT * FROM users WHERE id = ('
                    'SELECT user_id FROM tokens WHERE id = ? AND expired < ?'
                ')',
                (token, now))
            user = c.fetchone()
            return dict(zip(user.keys(), user))

