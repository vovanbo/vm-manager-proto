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


class DomainState(Enum):
    NOSTATE = 0         # no state
    RUNNING = 1         # the domain is running
    BLOCKED = 2         # the domain is blocked on resource
    PAUSED = 3          # the domain is paused by user
    SHUTDOWN = 4        # the domain is being shut down
    SHUTOFF = 5         # the domain is shut off
    CRASHED = 6         # the domain is crashed
    PMSUSPENDED = 7     # the domain is suspended by guest power management
    LAST = 8
