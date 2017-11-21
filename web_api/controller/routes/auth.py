import re
import datetime
from urllib.parse import urljoin
from flask import jsonify, Blueprint, url_for, current_app
from web_api.controller import security, errors, sms

bp = Blueprint('auth', __name__)

@bp.route('/provision/<number>')
def provision(number):

    number = re.sub('[^\d]','', number)
    iat = int(datetime.datetime.now().timestamp())
    exp = iat + 15

    payload = {
        'number': number,
        'iat': iat,
        'exp': exp
    }

    token = security.make_url_token(payload)
    url = url_for('.verify', token=token)
    url = urljoin(current_app.config['EXTERNAL_URL'], url)

    sms_client = sms.SMSClient.from_app(current_app)

    sms_client.send(
        to=number,
        message_text=url,
    )

    print(url)

    return jsonify({'message': 'success'})

@bp.route('/verify/<token>')
def verify(token):
    try:
        payload = security.parse_url_token(token)
    except:
        raise errors.AuthError('bad token')

    if payload['exp'] < int(datetime.datetime.now().timestamp()):
        raise errors.AuthError('token expired')

    return jsonify(payload)
