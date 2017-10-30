from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PhoneVerify(db.Model):
  __tablename__ = 'PHONE_VERIFY'
  phone_number = db.Column(db.String(15), primary_key=True, nullable=False, unique=True)
  code = db.Column(db.Integer, nullable=False, primary_key=False, unique=False)
  expires = db.Column(db.DateTime, nullable=False)


class User(db.Model):
  __tablename__ = 'USER'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  username = db.Column(db.String(30), primary_key=False, unique=True, nullable=False)
  password = db.Column(db.String(64), nullable=False)


def init(app):
  """
    - SqlAlchemy: Disable track modifications.
  """
  app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
  db.init_app(app)
  db.create_all()
