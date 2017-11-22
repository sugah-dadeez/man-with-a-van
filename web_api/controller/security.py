import jwt
import datetime
from itsdangerous import URLSafeSerializer
from flask import current_app, Blueprint
import bcrypt

class SecureBlueprint(Blueprint):
    def __init__(self):
        pass

def check_header_token():
    pass

def set_current_user():
    pass

def make_expiring_jwt(payload, exp=10):
    dt = int(datetime.datetime.now().timestamp())
    key = current_app.config['SECRET_KEY']

    return jwt.encode(
        dict(
            payload,
            iat=dt,
            exp=dt+exp
        ),
        key=key
    ).decode('utf-8')

def parse_url_token(token):
    s = get_url_token_serializer()
    return s.loads(token)

def make_url_token(data):
    s = get_url_token_serializer()
    return s.dumps(data)

def get_url_token_serializer():
    key = current_app.config['SECRET_KEY']
    return URLSafeSerializer(key)

def hash_password(password):
    return bcrypt.hashpw(password, bcrypt.gensalt())

def check_password_hash(hashed_password, password):
    return bcrypt.checkpw(password, hashed_password)
