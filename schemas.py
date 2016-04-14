from enum import Enum

from marshmallow import Schema, fields, pre_load, pre_dump
from marshmallow.validate import OneOf

from settings import USERINFO_ENDPOINTS, TaskStatus


class EnumField(fields.String):
    default_error_messages = {'invalid': 'Not a valid Enum.'}

    def __init__(self, *args, **kwargs):
        assert 'enum_class' in kwargs, 'enum_class parameter must be passed!'
        self._class = kwargs.pop('enum_class')
        self.to_value = kwargs.pop('to_value', True)
        super(EnumField, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        if not isinstance(value, Enum):
            self.fail('invalid')
        return value.value if self.to_value else value.name

    def _deserialize(self, value, attr, data):
        try:
            return self._class(value) if self.to_value else self._class[value]
        except ValueError:
            self.fail('invalid')


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


class TokenRequestSchema(Schema):
    provider = fields.String(
        required=True,
        validate=[OneOf(choices=USERINFO_ENDPOINTS.keys())]
    )
    access_token = fields.String(required=True)

    @pre_load
    def provider_to_lowercase(self, data):
        data['provider'] = data['provider'].lower()
        return data


class TokenResponseSchema(Schema):
    token = fields.String()
    user_id = fields.UUID()
    issued = fields.DateTime()
    expired = fields.DateTime()

    @pre_dump
    def fetch_token_field(self, data):
        if data.get('id'):
            data['token'] = data['id']
        return data


class TaskResponseSchema(Schema):
    id = fields.UUID(required=True)
    user_id = fields.UUID(required=True)
    command = fields.String(attribute='command_as_string')
    params = fields.String()
    result = fields.String()
    status = EnumField(enum_class=TaskStatus, to_value=False)
    created = fields.DateTime(required=True)
    started = fields.DateTime()
    finished = fields.DateTime()
