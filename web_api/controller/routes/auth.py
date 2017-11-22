import re
import datetime
from urllib.parse import urljoin
from flask import jsonify, Blueprint, url_for, current_app, request
from web_api.controller import security, errors, sms
from web_api.models import db, User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    body = request.json

    if 'username' not in body or 'password' not in body:
        raise errors.APIError('username and password required')

    u = db.session.query(User).filter_by(username=body['username']).first()

    errors.AuthError.raise_assert(u is not None) # check user exists
    errors.AuthError.raise_assert(u.check_password(body['password'])) # check password

    # TODO: check if jwt issued time is valid
    # can use this to invalidate old tokens that haven't expired yet

    # return session jwt
    token = security.make_expiring_jwt(
        payload={'username': u.username},
        exp=3600,
    )

    print(type(token))
    print(token)

    return jsonify({'token': token})

@bp.route('/signup', methods=['POST'])
def signup():
    body = request.json

    if 'username' not in body or 'password' not in body:
        raise errors.APIError('username and password required')

    u = db.session.query(User).filter_by(username=body['username']).first()

    if not u is None:
        raise errors.AuthError('user already exists')

    u = User(username=body['username'], is_verified=False)
    u.set_password(body['password'])

    db.session.add(u)
    db.session.commit()

    url = u.send_verification()

    return jsonify({'code': 'success', 'message': 'please verify phone'})

@bp.route('/send-verification/<username>', methods=['POST'])
def provision(username):

    u = db.session.query(User).filter_by(username=username).first()
    errors.AuthError.raise_assert(u is not None) # check user exists
    errors.AuthError.raise_assert(not u.is_verified, 'user already verified')
    url = u.send_verification()

    return jsonify({'message': 'success'})

@bp.route('/verify/<token>', methods=['POST'])
def verify(token):
    try:
        payload = security.parse_url_token(token)
    except:
        raise errors.AuthError('bad token')

    if payload['exp'] < int(datetime.datetime.now().timestamp()):
        raise errors.AuthError('token expired')

    u = db.session.query(User).filter_by(username=payload['username']).first()
    errors.AuthError.raise_assert(u is not None) # check if user exists

    u.is_verified = True
    db.session.add(u)
    db.session.commit()

    return jsonify({'message': 'success'})
