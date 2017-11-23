from flask import url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urljoin
from web_api.models import db
from web_api.controller import security, errors

class Job(db.Model):
    __tablename__ = 'JOB'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('USER.id'), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    list_date = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User')
    bids = db.relationship('JobBid')

    def to_dict(self, user=False, bids=False):
        output = {
            'id': self.id,
            'user_id': self.user_id,
            'is_active': self.is_active,
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
