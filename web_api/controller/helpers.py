import flask
import decimal, datetime, json
from web_api.controller import errors

class JSONEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            # Convert decimal instances to floats
            return float(round(obj,2))
        elif isinstance(obj, (datetime.datetime,datetime.date,datetime.time)):
            return obj.isoformat()

        return super(JSONEncoder, self).default(obj)

def make_boolean(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value = value.strip().lower()
        if value in ('true','false'):
            return value == 'true'

    raise errors.ValidationError('could not parse boolean "{}"'.format(value))
