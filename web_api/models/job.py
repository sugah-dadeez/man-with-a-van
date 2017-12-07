from flask import url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urljoin
from web_api.models import db
from web_api.controller import security, errors, sms

class Job(db.Model):
    __tablename__ = 'JOB'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('USER.id'), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    list_date = db.Column(db.DateTime, nullable=False)
    square_feet = db.Column(db.Numeric, nullable=False)
    pickup_address = db.Column(db.String())
    dropoff_address = db.Column(db.String())
    winning_bid = db.Column(db.Integer, nullable=True)

    user = db.relationship('User', uselist=False)
    bids = db.relationship('JobBid')

    def set_winning_bid(self, job_bid_id):
        # set is_active = false
        self.is_active = False
        self.winning_bid = job_bid_id

        sms_client = sms.SMSClient.from_app(current_app)

        winning_bid = None

        try:
            # send text to all drivers
            for bid in self.bids:
                if bid.id == job_bid_id:
                    msg = 'You won job {job_id}!\n\nContact user at {user_phone}\n\n-Haul Guys'.format(
                        job_id=self.id,
                        user_phone=self.user.username,
                    )

                    winning_bid = bid

                else:
                    msg = 'Sorry, you lost job {job_id}.\n\nBetter luck next time\n\n-Haul Guys'.format(
                        job_id=self.id,
                    )

                sms_client.send(
                    to=bid.driver.username,
                    message_text=msg,
                )

            # text users
            msg = 'Your drivers contact is {driver_phone}\n\n-Haul Guys'.format(
                driver_phone=winning_bid.driver.username
            )

            sms_client.send(
                to=self.user.username,
                message_text=msg,
            )

        except Exception as e:
            raise errors.APIError('failed to send sms')

    def to_dict(self, user=False, bids=False):
        output = {
            'id': self.id,
            'user_id': self.user_id,
            'is_active': self.is_active,
            'list_date': self.list_date,
            'square_feet': self.square_feet,
            'pickup_address': self.pickup_address,
            'dropoff_address': self.dropoff_address,
        }

        if bids:
            output['bids'] = [
                {
                    'id': b.id,
                    'driver': b.driver.to_dict(),
                    'amount': b.amount,
                    'bid_date': b.bid_date,
                    'is_active': b.is_active,
                }
                for b in self.bids
                if b.is_active
            ]

        return output


class JobBid(db.Model):
    __tablename__ = 'JOB_BID'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey('JOB.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('USER.id'))
    amount = db.Column(db.Numeric(), nullable=False)
    bid_date = db.Column(db.DateTime(), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    driver = db.relationship('User', uselist=False)
    job = db.relationship('Job', uselist=False)

    def to_dict(self, driver=False, job=False):
        output =  {
            'id': self.id,
            'job_id': self.job_id,
            'driver_id': self.driver_id,
            'amount': self.amount,
            'bid_date': self.bid_date,
            'is_active': self.is_active,
        }

        if driver:
            del output['driver_id']
            output['driver'] = self.driver.to_dict(bids=False, jobs=False)

        return output
