import datetime
import json
import os
import secrets
import shutil
import subprocess
import threading

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from werkzeug.security import generate_password_hash

lock = threading.Lock()

db = SQLAlchemy()
app = Flask(__name__)
# app.config['SECRET_KEY'] = "aaaaaaaaaaaaaa"
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['DATABASE_FILE'] = 'db.sqlite'

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:valera@winhost:5432/stin_cls"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['UPLOAD_FOLDER'] = '/upload'

res_dict = {}
recaptcha = None

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from .models import User


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


# blueprint for auth routes in our app
from .auth import auth as auth_blueprint

app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
from .main import main as main_blueprint

app.register_blueprint(main_blueprint)

from .admin import admin as admin_blueprint

app.register_blueprint(admin_blueprint)

db.init_app(app)
migrate = Migrate(app, db)

app_dir = os.path.dirname(os.path.dirname(__file__))

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

if not database_exists(engine.url):  # Checks for the first time
    create_database(engine.url)  # Create new DB
    print("New Database Created" + str(database_exists(engine.url)))  # Verifies if database is there or not.
    path_m = os.path.join(app_dir, 'migrations')
    if os.path.exists(path_m):
        shutil.rmtree(path_m)
    p = subprocess.Popen('flask --app StIn db init'.split(' '))
    p.communicate()
    p = subprocess.Popen('flask --app StIn db migrate'.split(' '))
    p.communicate()
    p = subprocess.Popen('flask --app StIn db upgrade'.split(' '))
    p.communicate()
    with app.app_context():
        with open('StIn/users.json') as f:
            users = json.load(f)
        for key in users.keys():
            test_user = User(username=key, password=generate_password_hash(users[key]), access=0,
                             date=datetime.datetime.now().replace(microsecond=0))
            db.session.add(test_user)
            db.session.commit()

# app_dir = os.path.dirname(os.path.dirname(__file__))
# database_path = os.path.join(app_dir, 'instance', app.config['DATABASE_FILE'])
# print(database_path)


# engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

# if not database_exists(engine.url):  # Checks for the first time

# with app.app_context():
#     create_database(engine.url)  # Create new DB
#     print("New Database Created" + str(database_exists(engine.url)))  # Verifies if database is there or not.
# if not os.path.exists(database_path):

# db.create_all()
# db.session.commit()
