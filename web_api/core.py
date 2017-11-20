import logging
from flask import Flask
from flask_cors import CORS
from .controller import routes, helpers, errors
from .models import db

def create_app(config, debug=False, testing=False, config_overrides=None):
    """
    :param config:
    :param debug:
    :param testing:
    :param config_overrides:
    :return:
    """

    app = Flask(__name__)

    # register default encoder
    app.json_encoder = helpers.JSONEncoder

    # register error handler
    errors.register_error_handlers(app)

    app.config.from_object(config)
    app.debug = debug
    app.testing = testing
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Configure logging
    # if not app.testing:
    #     logging.basicConfig(level=logging.INFO)

    # Setup the data models, clients
    with app.app_context():
    models.init(app)
    clients.init(app)

    # Register API Endpoints
    app.register_blueprint(api, url_prefix='/api')

    # register blueprints
    app.register_blueprint(routes.ping.bp, url_prefix='/ping')
    app.register_blueprint(routes.data.bp, url_prefix='/data')

    return app

def create_db():
    with app.app_context():
        db.create_all()
