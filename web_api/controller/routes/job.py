from flask import jsonify, g, request
from flask.views import MethodView
from web_api.controller import security, errors, helpers
from web_api.models import db, Job, JobBid
import datetime

bp = security.SecureBlueprint('job', __name__)

class JobView(MethodView):
    def get(self, id=None):
        if (id is not None):
            job = db.session.query(Job).filter_by(id=id).first()
            errors.QueryError.raise_assert(job is not None, 'job not found')
            return jsonify(job.to_dict(bids=True))
        else:
            jobs = db.session.query(Job).filter_by(is_active=True).all()
            return jsonify([job.to_dict() for job in jobs])


    def post(self):
        body = request.json

        job = Job(
            user_id=g.current_user.id,
            is_active=body.get('is_active', False),
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
        body = request.json
        job = db.session.query(Job).filter_by(id=id).first()
        errors.QueryError.raise_assert(job is not None, 'job not found')

        if 'winning_bid' in body:
            job_bid_id = body['winning_bid']
            job_bid = db.session.query(JobBid).filter_by(id=job_bid_id).first()
            print(job_bid_id, job_bid)
            errors.QueryError.raise_assert(job_bid is not None, 'job bid {} not found'.format(job_bid_id))
            job.set_winning_bid(job_bid_id)

        elif 'is_active' in body:
            errors.ValidationError.raise_assert(body['is_active'] in (True, False), 'is_active must be boolean')
            job.is_active = body.get('is_active')

        db.session.add(job)
        db.session.commit()

        return jsonify(job.to_dict(bids=True))

    def delete(self, id=None):
        pass

job_view = JobView.as_view('job_view')
bp.add_url_rule('/', view_func=job_view, methods=['POST','GET'])
bp.add_url_rule('/<int:id>', view_func=job_view, methods=['GET','PUT','PATCH','DELETE'])

# # TODO: convert to pluggable view

class JobBidView(MethodView):
    def get(self, job_id):

        job = db.session.query(Job).filter_by(id=job_id).first()
        errors.QueryError.raise_assert(job is not None, 'job not found')

        query = db.session.query(JobBid).filter_by(job_id=job_id)

        # restrict others users to only see their bids
        if not job.user_id == g.current_user.id:
            query = query.filter_by(driver_id=g.current_user.id)

        query = query.order_by(JobBid.bid_date.desc())

        if 'history' in request.args:
            history = helpers.make_boolean(request.args.get('history'))

            if history:
                jobbids = query.all()
                return jsonify([j.to_dict(driver=True, job=True) for j in jobbids])

        query = query.filter_by(is_active=True)

        if job.user_id == g.current_user.id:
            jobbids = query.all()
            return jsonify([j.to_dict(driver=True, job=True) for j in jobbids])

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
