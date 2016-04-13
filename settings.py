import os
from enum import Enum

BASE_DIR = os.path.dirname(__file__)
USERINFO_ENDPOINTS = {
    'google': {
        'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
        'additional_params': {},
        'schema': 'schemas.GoogleUserinfoSchema',
    },
    'facebook': {
        'url': 'https://graph.facebook.com/v2.5/me',
        'additional_params': {
            'fields': 'id,email,name,first_name,last_name,link,gender,picture,verified'
        },
        'schema': 'schemas.FacebookUserinfoSchema',
    }
}
UUID_PATTERN = '[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}'


class TaskStatus(Enum):
    CREATED = 0
    QUEUED = 1
    IN_PROGRESS = 2
    DONE = 3
    FAILED = 4
