from flask import jsonify, current_app, g
from werkzeug.exceptions import HTTPException, default_exceptions
import datetime
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    '''register all error handlers for this flask app'''
    # http://flask.pocoo.org/docs/0.12/api/#flask.Flask.register_error_handler

    # handler for python generic "Exceptions"
    app.register_error_handler(Exception, handle_exception)

    # explicitly handle all werkzeug exceptions
    for err in default_exceptions.values():
        app.register_error_handler(err, handle_werkzeug_exception)


def handle_werkzeug_exception(err):
    '''override the handler for werkzeug exceptions'''
    new_err = WerkzeugError.from_httperror(err)
    return handle_exception(new_err)


def handle_exception(err):
    '''generic error handler, to be registered for generic Exceptions'''

    # if it's a custom error, use our class method, else use a standard payload
    if isinstance(err, APIError):
        resp = err.to_resp()

    else:
        resp = jsonify({'code': 'api_failure', 'message': str(err)})
        resp.status_code = 500

    if current_app.config.get('RAISE_ERRORS'):
        logger.exception(err)
    else:
        logger.info(str(err))

    return resp


class APIError(Exception):
    '''general handled error'''
    status_code = 500
    message = 'internal api failure'
    error_code = 'api_failure'

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__(self)
        # super(Exception, self).__init__(message)

        if message is not None:
            self.message = message

        if status_code is not None:
            self.status_code = status_code

        self.payload = payload

    @classmethod
    def raise_assert(cls,bool,msg=None):
        if not bool:
            raise cls(msg)

    def to_dict(self):
        rv = {}
        if self.payload:
            rv.update(self.payload)

        rv['code'] = self.error_code
        rv['message'] = self.message

        return rv

    def to_resp(self):
        payload = self.to_dict()
        resp = jsonify(payload)
        resp.status_code = self.status_code
        return resp

    def __str__(self):
        return '{error_class}, {msg}'.format(
            error_class=self.__class__.__name__,
            # code=self.error_code,
            msg=self.message,
        )

class QueryError(APIError):
    '''custom error class for auth errors'''
    status_code = 400
    message = 'bad query'
    error_code = 'bad_query'

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__(message, status_code, payload)


class AuthError(APIError):
    '''custom error class for auth errors'''
    status_code = 401
    message = 'failed to authenticate'
    error_code = 'access_denied'

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__(message, status_code, payload)


class WerkzeugError(APIError):
    '''custom error class for werkzeug errors'''
    message = 'http error'
    error_code = 'http_exception'

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__(message, status_code, payload)

    @classmethod
    def from_httperror(cls, err):
        obj = cls(message=err.name, status_code=err.code)
        return obj


class LoginError(APIError):
    '''custom error class for auth errors'''
    status_code = 401
    message = 'Login failed.'
    error_code = 'login_failed'

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__(message, status_code, payload)


class EmailVerificationError(APIError):
    '''custom error class for email verify errors'''
    status_code = 401
    message = 'User email not verified.'
    error_code = 'email_not_verified'

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__(message, status_code, payload)

class PermissionsError(APIError):
    '''error class for bad permissions'''
    status_code = 401
    message = 'Insufficient permissions'
    error_code = 'insufficient_permissions'

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__(message, status_code, payload)


class ValidationError(APIError):
    '''error class for objects failing data validation'''
    status_code = 400
    message = 'data validation error'
    error_code = 'failed_data_validation'

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__(message, status_code, payload)
