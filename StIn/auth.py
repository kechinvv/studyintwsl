import json

import requests
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import logout_user, login_required, current_user, login_user

from .logger import add_log
from .models import User

auth = Blueprint('auth', __name__)

with open('StIn/captcha.json') as f:
    keys_captcha = json.load(f)

secret = keys_captcha['secret']
public = keys_captcha['public']

def is_human(captcha_response):
    payload = {'response': captcha_response, 'secret': secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']


@auth.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    captcha_response = request.form.get('g-recaptcha-response')
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        elif is_human(captcha_response):
            login_user(user, remember=remember)
            add_log(current_user.id, "Successful login {}".format(user.username), request.remote_addr)
            return redirect(url_for('main.index'))
        else:
            flash('Please, check captcha')
            return redirect(url_for('auth.login'))
    return render_template('login.html', title='Sign In', sitekey=public)


@auth.route('/logout')
@login_required
def logout():
    username = current_user.username
    id = current_user.id
    logout_user()
    add_log(id, "Successful logout {}".format(username), request.remote_addr)
    return redirect(url_for('auth.login'))
