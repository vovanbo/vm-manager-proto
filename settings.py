import os

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