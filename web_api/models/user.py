import bcrypt, datetime
from flask import url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urljoin
from web_api.models import db
from web_api.controller import security, sms

class User(db.Model):
    __tablename__ = 'USER'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), primary_key=False, unique=True, nullable=False)
    hashed_password = db.Column(db.String(64), nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)

    def set_password(self, password):
        '''hash via bcrypt and persist to user'''

        self.hashed_password = bcrypt.hashpw(
            password=password.encode('utf-8'),
            salt=bcrypt.gensalt()
        )

    def check_password(self, password):
        '''check password against hashed user pwd using bcrypt'''

        return bcrypt.checkpw(
            password=password.encode('utf-8'),
            hashed_password=self.hashed_password
        )

    def send_verification(self, exp=3600):
        iat = int(datetime.datetime.now().timestamp())

        payload = {
            'username': self.username,
            'iat': iat,
            'exp': iat + exp
        }

        token = security.make_url_token(payload)
        url = url_for('auth.verify', token=token)
        url = urljoin(current_app.config['EXTERNAL_URL'], url)

        sms_client = sms.SMSClient.from_app(current_app)

        sms_client.send(
            to=self.username,
            message_text=url,
        )

        return url
