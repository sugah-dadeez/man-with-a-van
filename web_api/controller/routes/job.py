from flask import jsonify, g, request
from flask.views import MethodView
from web_api.controller import security
from web_api.models import db, Job, JobBid
import datetime

bp = security.SecureBlueprint('job', __name__)

class JobView(MethodView):
    def get(self, job_id=None):
        print(job_id)
        job = db.session.query(Job).filter_by(id=job_id).first()
        print('job',job)
        return jsonify({'code': 'asdf'})
        # return jsonify(job.to_dict(bids=False))

    def post(self, job_id=None):

        body = request.json

        job = Job(
            user_id=g.current_user.id,
            is_active=True,
            list_date=datetime.datetime.now(),
        )

        db.session.add(job)
        db.session.commit()

        return jsonify(job.to_dict(bids=True))

    def put(self, job_id=None):
        pass

    def patch(self, job_id=None):
        pass

    def delete(self, job_id):
        pass

job_view = JobView.as_view('job_view')
bp.add_url_rule('/', view_func=job_view, methods=['GET','POST'])
bp.add_url_rule('/<int:job_id>', defaults={'job_id': None}, view_func=job_view, methods=['GET','PUT','PATCH','DELETE'])

# @bp.route('/', methods=['POST'])
# def create_job():
#     pass
#
# # TODO: convert to pluggable view
#
# @bp.route('/<id>', methods=['GET']))
# def get_job(id):
#     pass
#
# @bp.route('/<id>', methods=['PUT', 'PATCH'])
# def edit_job(id):
#     pass
#
# @bp.route('/<id>', methods=['DELETE'])
# def delete_job(id):
#     '''inactivates job, not a real delete'''
#     pass
#
# # TODO: convert to pluggable view
#
# @bp.route('/<id>/bid', methods=['GET'])
# def get_job_bid(id):
#     pass
