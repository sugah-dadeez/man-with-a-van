from flask import jsonify, Blueprint
from flask.views import MethodView

bp = Blueprint('job', __name__)

class Job(MethodView):
    def get(self, job_id=None):
        if job_id is None:
            pass
        else:
            pass

    def post(self):
        pass

    def put(self, job_id=None):
        pass

    def patch(self, job_id=None):
        pass

    def delete(self, job_id):
        pass

job_view = UserAPI.as_view('job_view')
bp.add_url_rule('/', defaults={'job_id': None}, view_func=job_view, methods=['GET',])
bp.add_url_rule('/<int:job_id>', defaults={'job_id': None}, view_func=job_view, methods=['GET','PUT','PATCH','DELETE'])
bp.add_url_rule('/', defaults={'job_id': None}, view_func=job_view, methods=['POST',])

@bp.route('/', methods=['POST'])
def create_job():
    pass

# TODO: convert to pluggable view

@bp.route('/<id>', methods=['GET']))
def get_job(id):
    pass

@bp.route('/<id>', methods=['PUT', 'PATCH'])
def edit_job(id):
    pass

@bp.route('/<id>', methods=['DELETE'])
def delete_job(id):
    '''inactivates job, not a real delete'''
    pass

# TODO: convert to pluggable view

@bp.route('/<id>/bid', methods=['GET'])
def get_job_bid(id):
    pass
