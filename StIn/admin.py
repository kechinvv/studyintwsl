import datetime
import os
from functools import wraps

from flask import Blueprint, flash, render_template, request, send_file
from flask import redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import asc
from werkzeug.security import generate_password_hash

from StIn import db
from StIn.logger import add_log
from StIn.models import Roles, User, UserLog
from StIn.works_handler import app_dir

admin = Blueprint('admin', __name__)


def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:  # the user is not logged in
                return redirect(url_for('auth.login'))

            if not current_user.allowed(access_level):
                add_log(current_user.id, "Try view users without access", request.remote_addr)
                flash('You do not have access to this resource.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@admin.route("/users")
@login_required
@requires_access_level(Roles.senior)
def users():
    if current_user.access == 0:
        users_list = User.query.order_by(User.date).all()
    elif current_user.access == 1:
        users_list = User.query.filter_by(access=Roles.junior.value).order_by(User.date).all()
    return render_template('users.html', users=users_list, roles={role.value: role.name for role in Roles})


@admin.route("/users/upload_user", methods=['POST'])
@login_required
@requires_access_level(Roles.senior)
def upload_user():
    access = Roles[request.form.get('role')].value
    if access <= current_user.access:
        add_log(current_user.id, "Try upload user without access", request.remote_addr)
        flash('You do not have access to this action.', 'danger')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        date = datetime.datetime.now().replace(microsecond=0)
        user = User(username=username, password=generate_password_hash(password), access=access, date=date)
        db.session.add(user)
        db.session.commit()
        add_log(current_user.id, "Upload user {}".format(username), request.remote_addr)
    return redirect(url_for('admin.users'))


@admin.route("/users/delete_user", methods=['POST'])
@login_required
@requires_access_level(Roles.senior)
def delete_user():
    delete_id = request.form.get('id')
    deleting_user = User.query.filter_by(id=delete_id).first()
    if deleting_user.access <= current_user.access:
        add_log(current_user.id, "Try delete user without access", request.remote_addr)
        flash('You do not have access to this action.', 'danger')
    else:
        db.session.delete(deleting_user)
        db.session.commit()
        add_log(current_user.id, "Delete user {}".format(deleting_user.username), request.remote_addr)
    return redirect(url_for('admin.users'))


@admin.route('/download_logs')
@login_required
@requires_access_level(Roles.senior)
def download_logs():
    user_id = int(request.args.get('user_id'))
    user = User.query.filter_by(id=user_id).first()
    if user.access < current_user.access:
        add_log(current_user.id, "Try download logs without access", request.remote_addr)
        flash('You do not have access to this action.', 'danger')
        return redirect(url_for('admin.users'))
    add_log(current_user.id, "Download logs for {}".format(user.username), request.remote_addr)
    path = os.path.join(app_dir, 'logs', f'user-{user_id}.txt')
    if not os.path.exists(path):
        with open(path, "a") as file:
            res = UserLog.query.filter_by(user_id=user_id).order_by(asc(UserLog.id)).all()
            for row in res:
                file.write("Date {}; {}; addr={}\n".format(row.date, row.action, row.addr))
    return send_file(path, mimetype='text/csv', download_name=f'user-{user_id}.txt', as_attachment=True)
