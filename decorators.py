import functools

from tornado.web import HTTPError


def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            self.send_error(401)
        return method(self, *args, **kwargs)
    return wrapper
