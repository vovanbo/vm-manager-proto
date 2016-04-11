from tornado.escape import json_decode
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    COOKIE_NAME = 'VMs_manager'

    def get_current_user(self):
        user_json = self.get_secure_cookie(self.COOKIE_NAME)
        if not user_json:
            return None
        return json_decode(user_json)