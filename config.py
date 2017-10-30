"""
This file contains all of the configuration values for the application.
Update this file with the values for your specific Google Cloud project.
You can create and manage projects at https://console.developers.google.com

man-with-a-van configuration based on this:
https://github.com/GoogleCloudPlatform/getting-started-python/blob/master/2-structured-data/config.py
"""

import json
import os

# The secret key is used by Flask to encrypt session cookies.
SECRET_KEY = 'secret'

with open("config.json") as config_file:
  config_params = json.load(config_file)
  # Google Cloud Project ID. This can be found on the 'Overview' page at
  # https://console.developers.google.com
  PROJECT_ID = config_params['PROJECT_ID']  # This should change
  # The Values below are used for Twilio SMS. Find them
  # at https://twilio.com/user/account
  TWILIO_ACCOUNT_SID = config_params['TWILIO_ACCOUNT_SID']
  TWILIO_AUTH_TOKEN = config_params['TWILIO_AUTH_TOKEN']
  TWILIO_FROM_NUMBER = config_params['TWILIO_FROM_NUMBER']
  # CloudSQL & SQLAlchemy configuration
  # Replace the following values the respective values of your Cloud SQL
  # instance.
  CLOUDSQL_USER = config_params['CLOUDSQL_USER']
  CLOUDSQL_PASSWORD = config_params['CLOUDSQL_PASSWORD']
  CLOUDSQL_DATABASE = config_params['CLOUDSQL_DATABASE']
  # Set this value to the Cloud SQL connection name, e.g.
  #   "project:region:cloudsql-instance".
  # You must also update the value in app.yaml.
  CLOUDSQL_CONNECTION_NAME = config_params['CLOUDSQL_CONNECTION_NAME']


# The CloudSQL proxy or locally installed MySql database. CloudSQL proxy is
# started by:
#     ./cloud_sql_proxy -instances=secure-outpost-166114:us-central1:manwithavan=tcp:3306 &

LOCAL_SQLALCHEMY_DATABASE_URI = (
  'mysql+pymysql://{user}:{password}@127.0.0.1:3306/{database}').format(
  user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD,
  database=CLOUDSQL_DATABASE)

# When running on App Engine a unix socket is used to connect to the cloudsql
# instance.
LIVE_SQLALCHEMY_DATABASE_URI = (
  'mysql+pymysql://{user}:{password}@localhost/{database}'
  '?unix_socket=/cloudsql/{connection_name}').format(
  user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD,
  database=CLOUDSQL_DATABASE, connection_name=CLOUDSQL_CONNECTION_NAME)

if os.environ.get('GAE_INSTANCE'):
  SQLALCHEMY_DATABASE_URI = LIVE_SQLALCHEMY_DATABASE_URI
else:
  SQLALCHEMY_DATABASE_URI = LOCAL_SQLALCHEMY_DATABASE_URI
