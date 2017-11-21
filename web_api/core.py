import logging
import os
import yaml
from flask import Flask
from flask_cors import CORS
from .controller import routes, helpers, errors
from .models import db

def create_app(debug=False, raise_errors=False):
    """
    :param config:
    :param debug:
    :return:
    """

    app = Flask(__name__)

    # register default encoder
    app.json_encoder = helpers.JSONEncoder

    # register error handler
    errors.register_error_handlers(app)

    configure_app(app)
    # app.config.from_object(config)
    app.debug = debug
    app.config['RAISE_ERRORS'] = raise_errors
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'secret_key'

    db.init_app(app)

    # Configure logging
    # if not app.testing:
    #     logging.basicConfig(level=logging.INFO)

    # register blueprints
    app.register_blueprint(routes.ping.bp, url_prefix='/ping')
    app.register_blueprint(routes.auth.bp, url_prefix='/auth')

    return app

def configure_app(app):
    assert 'FLASK_CONFIG' in os.environ, 'missing FLASK_CONFIG in environment'
    fp = os.environ.get('FLASK_CONFIG')

    with open(fp, 'r') as f:
        conf_obj = yaml.load(f)

    app.config['EXTERNAL_URL'] = conf_obj['external_url']
    app.config['SQLALCHEMY_DATABASE_URI'] = conf_obj['db']['url']
    app.config['TWILIO_ACCOUNT_SID'] = conf_obj['twilio']['account_sid']
    app.config['TWILIO_AUTH_TOKEN'] = conf_obj['twilio']['auth_token']
    app.config['TWILIO_FROM_NUMBER'] = conf_obj['twilio']['from_number']

def reset_db():
    app = create_app()
    with app.app_context():
        db.create_all()
