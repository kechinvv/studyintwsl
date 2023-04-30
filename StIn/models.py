import enum
import json

from flask_login import UserMixin
from werkzeug.security import check_password_hash

from . import db


class MTypes(enum.Enum):
    pytorch = "PyTorch"
    keras = "Keras"
    script = "Script"


class Roles(enum.IntEnum):
    owner = 0
    senior = 1
    junior = 2


class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(300))
    addr = db.Column(db.String(50))
    date = db.Column(db.DateTime)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(64))
    access = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    logs = db.relationship("UserLog", backref='user')

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

    def allowed(self, access_level):
        return self.access <= access_level

    # Required for administrative interface
    def __unicode__(self):
        return self.username


class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
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
    name = db.Column(db.String(50), unique=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'))
    language = db.Column(db.String(120))
    state = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime)
    cpu = db.Column(db.Float, default=0)
    ram = db.Column(db.Float, default=0)
    gpu = db.Column(db.JSON, default=json.dumps([(0, 0)]))
    time = db.Column(db.Float, default=0)
    exc = db.Column(db.String(50), default='-')
    stats = db.relationship("Statistic", backref='work')


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    first = db.Column(db.String(4), nullable=False)
    token_hash = db.Column(db.String(64), nullable=False)
    date = db.Column(db.DateTime)
