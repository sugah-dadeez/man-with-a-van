from flask import jsonify, g, request
from flask.views import MethodView
from web_api.controller import security, errors
from web_api.models import db, User
import datetime

bp = security.SecureBlueprint('user', __name__)

class UserView(MethodView):
    def get(self, id=None):
        if not id:
            id=g.current_user.id

        user = db.session.query(User).filter_by(id=id).first()
        errors.QueryError.raise_assert(user is not None, 'user not found')
        return jsonify(user.to_dict(bids=True, jobs=True))

    def post(self):
        pass

    def put(self, id=None):
        pass

    def patch(self, id=None):
        pass

    def delete(self, id=None):
        pass

job_view = UserView.as_view('job_view')

bp.add_url_rule('/', view_func=job_view, methods=['GET', 'PATCH'])
bp.add_url_rule('/<int:id>', view_func=job_view, methods=['GET', 'PATCH'])
