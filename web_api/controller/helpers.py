import flask
import decimal, datetime, json

class JSONEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            # Convert decimal instances to floats
            return float(round(obj,2))
        elif isinstance(obj, (datetime.datetime,datetime.date,datetime.time)):
            return obj.isoformat()

        return super(JSONEncoder, self).default(obj)
