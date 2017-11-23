import jwt
import datetime
from functools import wraps
from itsdangerous import URLSafeSerializer
from flask import current_app, Blueprint, request, g
from web_api.controller import errors
from web_api.models import db, User


class SecureBlueprint(Blueprint):
    '''subclass of flask Blueprint that enforces auth on all routes'''
    def __init__(self, *args, **kwargs):
        Blueprint.__init__(self,  *args, **kwargs)
        self.before_request(set_token_user)

def decode_token(token):
    app = current_app
    key = app.config['SECRET_KEY']

    # assert client_id, 'missing client id'
    assert key, 'missing public key'

    try:
        payload = jwt.decode(
            jwt=token,
            key=key,
        )

    except jwt.ExpiredSignature:
        raise errors.AuthError('token expired')

    except jwt.InvalidAudienceError:
        raise errors.AuthError('incorrect token audience')

    except jwt.DecodeError:
        raise errors.AuthError('invalid token signature')

    except Exception as e:
        raise errors.AuthError('authentication failed')

    return payload

def set_token_user():
    auth = request.headers.get('Authorization', None)
    errors.AuthError.raise_assert(auth is not None, 'auth header missing')

    parts = auth.strip().split()
    errors.AuthError.raise_assert(parts[0].lower()=='bearer', 'bad authorization header')
    errors.AuthError.raise_assert(len(parts) == 2, 'malformed authorization header')

    token = parts[1]
    token_info = decode_token(token)

    username = token_info['username']
    u = db.session.query(User).filter_by(username=username).first()
    errors.AuthError.raise_assert(u is not None, 'user not found')
    errors.AuthError.raise_assert(u.is_verified, 'user not verified')

    g.current_token = token
    g.current_token_info = token_info
    g.current_user = u

def requires_auth(f):
    '''decorator to enforce jwt auth on route and set g.user'''
    @wraps(f)
    def decorated(*args, **kwargs):
        set_token_user()
        return f(*args, **kwargs)
    return decorated


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
