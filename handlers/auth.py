import logging
import uuid
from datetime import datetime

from tornado import gen
from tornado.escape import json_decode, to_basestring
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat
from tornado.options import options

from handlers.base import BaseHandler
from schemas import TokenRequestSchema, TokenResponseSchema
from settings import USERINFO_ENDPOINTS
from utils import module_member, generate_token


class TokenHandler(BaseHandler):
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    @gen.coroutine
    def post(self):
        data, errors = TokenRequestSchema().loads(
            self.request.body.decode('utf-8'))

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
            self.send_error(400, message='Authentication server error',
                            errors=errors)
            return
        else:
            logging.info(json_decode(response.body))

        schema = module_member(provider['schema'])()
        userinfo, errors = schema.loads(to_basestring(response.body))

        if errors:
            self.send_error(400, message='Wrong authentication data received',
                            errors=errors)
            return

        account = self.db.execute(
            'SELECT * FROM accounts WHERE provider = ? AND sub = ?',
            (data['provider'], userinfo['sub'], )
        ).fetchone()

        if account:
            user = self.db.execute(
                'SELECT * FROM users WHERE email = ?', (account['email'], )
            ).fetchone()
            if not user:
                self.send_error(500, message='DB error. User not found.')
                return
        else:
            user = {
                'id': str(uuid.uuid4()),
                'email': userinfo['email']
            }
            self.db.execute(
                'INSERT INTO users (id, email) VALUES (:id, :email)', user)

            account = {
                'user_id': user['id'],
                'provider': data['provider']
            }
            account.update(userinfo)
            self.db.execute(
                'INSERT INTO '
                'accounts (user_id, provider, sub, email, email_verified, name, given_name, family_name, profile, picture, gender) '
                'VALUES (:user_id, :provider, :sub, :email, :email_verified, :name, :given_name, :family_name, :profile, :picture, :gender)',
                account
            )
            self.db.commit()

        now = datetime.utcnow()
        token = {
            'id': generate_token(options.token_length),
            'user_id': user['id'],
            'issued': now,
            'expired': now + options.token_expire_time
        }
        self.db.execute(
            'INSERT INTO tokens (id, user_id, issued, expired) '
            'VALUES (:id, :user_id, :issued, :expired)',
            token
        )
        self.db.commit()

        self.finish(TokenResponseSchema().dumps(token).data)
