import hashlib
import random as ra
import string as st
from datetime import datetime, timedelta

from flask import request, make_response, Blueprint, jsonify

from .clients import twilio_client
from .models import db, PhoneVerify, User

api = Blueprint('api', __name__)


@api.route("/phone-registration", methods=["POST"])
def phone_registration():
  """

  :return:
  """
  json = request.get_json()

  phone_number = json['PhoneNumber']
  random_code = ra.randrange(0, 99999)
  expires = datetime.now() + timedelta(minutes=10)

  if not PhoneVerify.query.filter_by(phone_number=phone_number).update(dict(code=random_code,
                                                                            expires=expires)):
    db.session.add(PhoneVerify(phone_number=phone_number,
                               code=random_code,
                               expires=expires))
  db.session.commit()

  message_text = "Your Man With A Van Verification Code is %05d" % random_code

  twilio_client.send_sms(message_text, phone_number)

  return make_response("", 200)


@api.route("/verify-phone", methods=["POST"])
def verify_phone():
  """

  :return:
  """
  json = request.get_json()
  verification_code = json['VerificationCode']
  phone_number = json['PhoneNumber']

  phone_verify_query = PhoneVerify.query.filter_by(phone_number=phone_number,
                                                   code=verification_code)

  phone_verify = phone_verify_query.with_for_update().first()

  if phone_verify and phone_verify.expires > datetime.now():  # If the verification code is valid...
    phone_verify_query.update(dict(expires=datetime.now()))  # ... expire it.
    # Randomly generate a password for this user,
    new_password = ''.join(ra.SystemRandom().choice(st.printable) for _ in range(30))

    # Hash, then make Hex string
    pass_hash = hashlib.pbkdf2_hmac('sha256', bytes(new_password, encoding='utf-8'), b"", 10000).hex()

    # Create or update the user, and pass password back to the client.
    if not User.query.filter_by(username=phone_number).update(dict(password=pass_hash)):
      db.session.add(User(id=None,
                          username=phone_number,
                          password=pass_hash))

    db.session.commit()

    return make_response(jsonify(password=new_password), 200)
  else:
    return make_response("", 404)
