from flask import jsonify, g, request
from flask.views import MethodView
from web_api.controller import security, errors
from web_api.models import db, Job, JobBid
import datetime

bp = security.SecureBlueprint('job', __name__)

class JobView(MethodView):
    def get(self, id=None):
        job = db.session.query(Job).filter_by(id=id).first()
        errors.QueryError.raise_assert(job is not None, 'job not found')
        return jsonify(job.to_dict(bids=True))

    def post(self):
        body = request.json

        job = Job(
            user_id=g.current_user.id,
            is_active=True,
            list_date=datetime.datetime.now(),
            square_feet=body.get('square_feet'),
            pickup_address=body.get('pickup_address'),
            dropoff_address=body.get('dropoff_address'),
        )

        db.session.add(job)
        db.session.commit()

        return jsonify(job.to_dict(bids=True))

    def put(self, id=None):
        pass

    def patch(self, id=None):
        pass

    def delete(self, id=None):
        pass

job_view = JobView.as_view('job_view')
bp.add_url_rule('/', view_func=job_view, methods=['POST'])
bp.add_url_rule('/<int:id>', view_func=job_view, methods=['GET','PUT','PATCH','DELETE'])

# # TODO: convert to pluggable view

class JobBidView(MethodView):
    def get(self, job_id):

        query = db.session.query(JobBid).filter_by(
            job_id=job_id,
            driver_id=g.current_user.id,
        )

        query = query.order_by(JobBid.bid_date.desc())

        if 'history' in request.args:
            history = request.args.get('history').lower().strip()

            errors.QueryError.raise_assert(
                history in ('true','false'),
                'bad history argument'
            )

            if history == 'true':
                jobbids = query.all()
                return jsonify([j.to_dict(driver=True, job=True) for j in jobbids])


        query = query.filter_by(is_active=True)
        jobbid = query.first()

        errors.QueryError.raise_assert(jobbid is not None, 'no active bid on this job')
        return jsonify(jobbid.to_dict(driver=True, job=True))


    def post(self, job_id):
        body = request.json

        errors.PermissionsError.raise_assert(g.current_user.is_driver, 'must be driver to post bid')

        # ensure job exists
        job = db.session.query(Job).filter_by(id=job_id).first()
        errors.QueryError.raise_assert(job is not None, 'job not found')

        # make sure no existing bids from this user
        old_bids = db.session.query(JobBid).filter_by(
            job_id=job_id,
            driver_id=g.current_user.id,
        ).all()

        if len(old_bids) > 0:
            for bid in old_bids:
                bid.is_active = False
                db.session.add(bid)

        bid = JobBid(
            driver_id = g.current_user.id,
            amount = body['amount'],
            bid_date = datetime.datetime.now(),
            is_active = True
        )

        job.bids.append(bid)
        db.session.add(job)

        db.session.commit()

        return jsonify(bid.to_dict(driver=True, job=True))

    def delete(self, job_id):
        jobbid = db.session.query(JobBid).filter_by(
            job_id=job_id,
            driver_id=g.current_user.id,
        ).first()
        errors.QueryError.raise_assert(jobbid is not None, 'job bid not found')
        db.session.delete(jobbid)
        db.session.commit()
        return jsonify(jobbid.to_dict())

    def patch(self, job_id, job_bid_id):
        body = request.json
        job = db.session.query(Job).filter_by(job_id=job_id, id=job_bid_id).first()
        errors.QueryError.raise_assert(job is not None, 'job not found')


jobbid_view = JobBidView.as_view('job_bid_view')
bp.add_url_rule(
    '/<int:job_id>/bid/',
    view_func=jobbid_view,
    methods=['GET','PUT','PATCH','DELETE'],
)
bp.add_url_rule(
    '/<int:job_id>/bid/',
    view_func=jobbid_view,
    methods=['GET','POST'],
)
