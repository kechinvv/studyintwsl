import json

from flask_login import UserMixin
from werkzeug.security import check_password_hash
import enum

from . import db


class MTypes(enum.Enum):
    pytorch = "PyTorch"
    keras = "Keras"
    script = "Script"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(64))

    # Flask-Login integration
    # NOTE: is_authenticated, is_active, and is_anonymous
    # are methods in Flask-Login < 0.3.0
    @property
    def is_authenticated(self):
        return True

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username


class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    worker_path = db.Column(db.String(150))
    pip_path = db.Column(db.String(150))
    type = db.Column(db.Enum(MTypes))
    date = db.Column(db.DateTime)
    works = db.relationship('Work', backref='worker')


class Statistic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_id = db.Column(db.Integer, db.ForeignKey('work.id'))
    cpu = db.Column(db.Float, default=0)
    ram = db.Column(db.Float, default=0)
    gpu = db.Column(db.JSON, default=json.dumps([(0, 0)]))
    time = db.Column(db.Float, default=0)
    dtw = db.Column(db.JSON)
    res = db.Column(db.JSON)
    date = db.Column(db.DateTime)


class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'))
    language = db.Column(db.String(120))
    state = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime)
    cpu = db.Column(db.Float, default=0)
    ram = db.Column(db.Float, default=0)
    gpu = db.Column(db.JSON, default=json.dumps([(0, 0)]))
    time = db.Column(db.Float, default=0)
    stats = db.relationship("Statistic", backref='work')


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    first = db.Column(db.String(4), nullable=False)
    token_hash = db.Column(db.String(64), nullable=False)
    date = db.Column(db.DateTime)
