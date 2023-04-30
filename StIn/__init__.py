import datetime
import json
import os
import secrets

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
app = None
res_dict = {}


def create_app():
    global app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "aaaaaaaaaaaaaa"
    # app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['DATABASE_FILE'] = 'db.sqlite'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
    app.config['UPLOAD_FOLDER'] = '/upload'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    app_dir = os.path.dirname(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, 'instance', app.config['DATABASE_FILE'])
    print(database_path)
    if not os.path.exists(database_path):
        with app.app_context():
            db.create_all()
            db.session.commit()
            # passwords are hashed, to use plaintext passwords instead:
            # test_user = User(login="test", password="test")
            with open('StIn/users.json') as f:
                users = json.load(f)
            for key in users.keys():
                test_user = User(username=key, password=generate_password_hash(users[key]), access=0,
                                 date=datetime.datetime.now().replace(microsecond=0))
                db.session.add(test_user)
                db.session.commit()

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main_page import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    return app
