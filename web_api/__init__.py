import logging

from flask import Flask


def create_app(config, debug=False, testing=False, config_overrides=None):
  """

  :param config:
  :param debug:
  :param testing:
  :param config_overrides:
  :return:
  """

  app = Flask(__name__)

  app.config.from_object(config)
  app.debug = debug
  app.testing = testing

  # Configure logging
  if not app.testing:
    logging.basicConfig(level=logging.INFO)

  from . import models
  from . import clients
  # Setup the data models, clients
  with app.app_context():
    models.init(app)
    clients.init(app)

  # Register API Endpoints
  from .endpoints import api
  app.register_blueprint(api, url_prefix='/api')

  return app
