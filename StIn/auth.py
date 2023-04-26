from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import logout_user, login_required, current_user, login_user

from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        else:
            login_user(user, remember=remember)
            return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
