import logging
import uuid
from datetime import datetime

from tornado import gen
from tornado.escape import json_decode, json_encode
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat
from tornado.options import options

from handlers.base import BaseHandler
from schemas import TokenInSchema, TokenOutSchema
from settings import USERINFO_ENDPOINTS
from utils import module_member, generate_token


class TokenHandler(BaseHandler):
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    @gen.coroutine
    def post(self):
        data, errors = TokenInSchema().loads(self.request.body.decode('utf-8'))

        if errors:
            self.send_error(400, message='Wrong input parameters',
                            errors=errors)
            return

        provider = USERINFO_ENDPOINTS[data['provider']]
        query_params = {'access_token': data['access_token']}
        query_params.update(provider['additional_params'])
        userinfo_url = url_concat(provider['url'], query_params)
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(userinfo_url, raise_error=False)
        if response.error:
            errors = json_decode(response.body) if response.body else None
            self.send_error(401, message='Authentication server error',
                            errors=errors)
            return
        else:
            logging.info(json_decode(response.body))

        schema = module_member(provider['schema'])()
        userinfo, errors = schema.load(json_decode(response.body))

        if errors:
            self.send_error(401, message='Wrong authentication data received',
                            errors=errors)
            return

        c = self.application.db.cursor()
        c.execute(
            'SELECT * FROM users WHERE email = ?', (userinfo['email'], ))
        user = c.fetchone()
        if user:
            user = dict(zip(user.keys(), user))
        else:
            new_user_id = str(uuid.uuid4())
            user = {
                'id': new_user_id,
                'email': userinfo['email']
            }
            c.execute('INSERT INTO users (id, email) VALUES (:id, :email)',
                      user)

        c.execute(
            'SELECT * FROM accounts '
            'WHERE provider = ? AND sub = ? AND email = ?',
            (data['provider'], userinfo['sub'], userinfo['email'])
        )
        account = c.fetchone()
        if not account:
            account = {
                'user_id': user['id'],
                'provider': data['provider']
            }
            account.update(userinfo)
            c.execute(
                'INSERT INTO '
                'accounts (user_id, provider, sub, email, email_verified, name, given_name, family_name, profile, picture, gender) '
                'VALUES (:user_id, :provider, :sub, :email, :email_verified, :name, :given_name, :family_name, :profile, :picture, :gender)',
                account
            )
            self.application.db.commit()
        else:
            # TODO: Update account with data from OAuth2 provider
            account = dict(zip(account.keys(), account))

        now = datetime.utcnow()
        token = {
            'id': generate_token(options.token_length),
            'user_id': user['id'],
            'issued': now,
            'expired': now + options.token_expire_time
        }
        c.execute(
            'INSERT INTO '
            'tokens (id, user_id, issued, expired) '
            'VALUES (:id, :user_id, :issued, :expired)',
            token
        )
        self.application.db.commit()

        self.finish(TokenOutSchema().dumps(token).data)
