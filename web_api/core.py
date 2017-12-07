import logging
import os
import yaml
from flask import Flask
from flask_cors import CORS
from .controller import routes, helpers, errors
from .models import db

logger = logging.getLogger(__name__)

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

    # set debug mode
    app.debug = debug

    # configure logging
    configure_logging(debug=debug)

    # configure app
    app.config['RAISE_ERRORS'] = raise_errors
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    configure_app(app=app)

    # bind database
    db.init_app(app)

    # register blueprints
    app.register_blueprint(routes.ping.bp, url_prefix='/ping')
    app.register_blueprint(routes.auth.bp, url_prefix='/auth')
    app.register_blueprint(routes.job.bp, url_prefix='/job')
    app.register_blueprint(routes.user.bp, url_prefix='/user')

    with app.app_context():
        db.create_all()

    return app

def configure_app(app):
    assert 'FLASK_CONFIG' in os.environ, 'missing FLASK_CONFIG in environment'
    fp = os.environ.get('FLASK_CONFIG')

    if (not os.path.exists(fp)):
        logger.debug('CANNOT FIND FLASK CONFIG "{fp}"'.format(fp=fp))
    # assert, 'bad flask config "fp"'
    logger.debug('reading config "{fp}"'.format(fp=fp))


    with open(fp, 'r') as f:
        conf_obj = yaml.load(f)

    if 'secret_key' in conf_obj:
        app.config['SECRET_KEY'] = conf_obj['secret_key']
    else:
        logger.critical('no flask secret key set!')
        app.config['SECRET_KEY'] = 'secret_key'

    app.config['EXTERNAL_URL'] = conf_obj['external_url']
    app.config['SQLALCHEMY_DATABASE_URI'] = conf_obj['db']['url']
    app.config['TWILIO_ACCOUNT_SID'] = conf_obj['twilio']['account_sid']
    app.config['TWILIO_AUTH_TOKEN'] = conf_obj['twilio']['auth_token']
    app.config['TWILIO_FROM_NUMBER'] = conf_obj['twilio']['from_number']

def configure_logging(debug=False):
    # logging.basicConfig(level=logging.INFO)

    root = logging.getLogger()
    h = logging.StreamHandler()
    fmt = logging.Formatter(
        fmt='%(asctime)s %(levelname)s (%(name)s) %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
    h.setFormatter(fmt)

    root.addHandler(h)

    if debug:
        root.setLevel(logging.DEBUG)
    else:
        root.setLevel(logging.INFO)


def reset_db():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
