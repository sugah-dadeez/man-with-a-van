import bcrypt, datetime
from flask import url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urljoin
from web_api.models import db
from web_api.controller import security, errors, sms

class User(db.Model):
    __tablename__ = 'USER'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), primary_key=False, unique=True, nullable=False)
    hashed_password = db.Column(db.String(64), nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_driver = db.Column(db.Boolean, nullable=False, default=False)
    last_login_date = db.Column(db.DateTime, nullable=True)

    jobs = db.relationship('Job')
    bids = db.relationship('JobBid')

    def to_dict(self, bids=False, jobs=False):
        output = {
            'id': self.id,
            'username': self.username,
            'is_verified': self.is_verified,
            'is_driver': self.is_driver,
        }

        if bids:
            output['bids'] = [
                {
                    'id': b.id,
                    'job_id': b.job_id,
                    'amount': b.amount,
                    'bid_date': b.bid_date,
                    'is_active': b.is_active,
                }
                for b in self.bids
                if b.job.is_active
            ]

        if jobs:
            output['jobs'] = [j.to_dict() for j in self.jobs]

        return output

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

        try:
            sms_client.send(
                to=self.username,
                message_text=url,
            )

            print(url)
        except:
            raise errors.APIError('failed to send sms')

        return url
