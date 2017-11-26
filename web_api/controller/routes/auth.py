import re
import datetime
from urllib.parse import urljoin
from flask import jsonify, Blueprint, url_for, current_app, request, g
from web_api.controller import security, errors, sms
from web_api.models import db, User
from flask import logging

bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@bp.route('/check_token')
@security.requires_auth
def check_token():
    return jsonify({
        'token': g.current_token,
        'token_info': g.current_token_info,
        'user': g.current_user.username,
    })


@bp.route('/login', methods=['POST'])
def login():
    logger.info('logging in')

    body = request.json

    if 'username' not in body or 'password' not in body:
        raise errors.APIError('username and password required')

    u = db.session.query(User).filter_by(username=body['username']).first()

    errors.AuthError.raise_assert(u is not None) # check user exists
    errors.AuthError.raise_assert(u.check_password(body['password'])) # check password
    errors.AuthError.raise_assert(u.is_verified, 'user not verified') # check verified

    u.last_login_date = datetime.datetime.now()
    db.session.add(u)
    db.session.commit()

    # return session jwt
    token = security.make_expiring_jwt(
        payload={'username': u.username},
        exp=3600,
    )

    return jsonify({'token': token})

@bp.route('/signup', methods=['POST'])
def signup():
    body = request.json

    if 'username' not in body or 'password' not in body:
        raise errors.APIError('username and password required')

    u = db.session.query(User).filter_by(username=body['username']).first()

    if not u is None:
        raise errors.AuthError('user already exists')

    u = User(
        username=body['username'],
        is_verified=body.get('is_verified', False),
        is_driver=body.get('is_driver', False),
        minimum_iat=datetime.datetime.now().timestamp(),
    )
    u.set_password(body['password'])

    db.session.add(u)
    db.session.commit()

    if not u.is_verified:
        url = u.send_verification()

    return jsonify({'code': 'success'})

@bp.route('/send-verification/<username>', methods=['POST'])
def provision(username):

    u = db.session.query(User).filter_by(username=username).first()
    errors.AuthError.raise_assert(u is not None) # check user exists
    errors.AuthError.raise_assert(not u.is_verified, 'user already verified')
    url = u.send_verification()

    return jsonify({'message': 'success'})

@bp.route('/verify/<token>', methods=['GET', 'POST'])
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
