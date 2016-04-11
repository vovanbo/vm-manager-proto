from marshmallow import Schema, fields, pre_load, pre_dump
from marshmallow.validate import OneOf

from settings import USERINFO_ENDPOINTS


class GoogleUserinfoSchema(Schema):
    sub = fields.String(required=True)
    email = fields.Email(required=True)
    email_verified = fields.Boolean()
    name = fields.String()
    given_name = fields.String()
    family_name = fields.String()
    profile = fields.URL()
    picture = fields.URL()
    gender = fields.String()


class FacebookUserinfoSchema(Schema):
    sub = fields.String(required=True, load_from='id')
    email = fields.Email(required=True)
    email_verified = fields.Boolean(load_from='verified')
    name = fields.String()
    given_name = fields.String(load_from='first_name')
    family_name = fields.String(load_from='last_name')
    profile = fields.URL(load_from='link')
    picture = fields.URL()
    gender = fields.String()

    @pre_load
    def picture_url_conversion(self, data):
        data['picture'] = data['picture']['data']['url']
        return data


class TokenInSchema(Schema):
    provider = fields.String(
        required=True,
        validate=[OneOf(choices=USERINFO_ENDPOINTS.keys())]
    )
    access_token = fields.String(required=True)

    @pre_load
    def normalize_arguments(self, data):
        data = {k: v[0] for k, v in data.items()}
        data['provider'] = data['provider'].lower()
        return data


class TokenOutSchema(Schema):
    token = fields.String()
    user_id = fields.UUID()
    issued = fields.DateTime()
    expired = fields.DateTime()

    @pre_dump
    def fetch_token_field(self, data):
        if data.get('id'):
            data['token'] = data['id']
        return data