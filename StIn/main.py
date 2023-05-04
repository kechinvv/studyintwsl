import datetime
import json
import os
import shutil

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort, flash, send_file
from flask_login import login_required, current_user
from sqlalchemy import asc
from werkzeug.security import generate_password_hash, check_password_hash

from StIn.models import MTypes, Worker, Work, Token, Statistics
from . import app, db, lock
from .logger import add_log
from .works_handler import get_lvl, app_dir, create_model, delete_model

main = Blueprint('main', __name__)


@app.before_first_request
def state_init():
    works_list = Work.query.all()
    for work in works_list:
        if work.state:
            try:
                create_model(work)
            except Exception:
                work.state = False
                db.session.commit()


@main.route('/')
@login_required
def index():
    workers_list = []
    works_list = []
    try:
        workers_list = Worker.query.order_by(Worker.date).all()
        works_list = Work.query.order_by(Work.date).all()
        if 'my_message' in request.args:
            my_msg = request.args['my_message']
            flash(my_msg)
    except Exception as e:
        flash(str(e))
    finally:
        return render_template('index.html', works=works_list, workers=workers_list)


@main.route('/workers')
@login_required
def workers():
    selected = None
    workers_list = []
    try:
        if 'worker_id' in request.args:
            selected = request.args['worker_id']
        workers_list = Worker.query.order_by(Worker.date).all()
    except Exception as e:
        flash(str(e))
    finally:
        return render_template('workers.html', types=[type.value for type in MTypes], workers=workers_list,
                               worker_id=selected)


@main.route('/tokens')
@login_required
def tokens():
    tokens_list = []
    try:
        tokens_list = Token.query.order_by(Token.date).all()
    except Exception as e:
        flash(str(e))
    finally:
        return render_template('tokens.html', tokens=tokens_list)


@main.route('/works/upload_work', methods=['POST'])
@login_required
def upload_work():
    try:
        name = request.form.get('name')
        worker_id = request.form.get('worker')
        language = request.form.get('language')
        date = datetime.datetime.now().replace(microsecond=0)
        work = Work(name=name, worker_id=worker_id, date=date, language=language)
        db.session.add(work)
        db.session.commit()
        add_log(current_user.id, "Upload job {}".format(name), request.remote_addr)
    except Exception as e:
        flash(str(e))
    finally:
        return redirect(url_for('main.index'))


@main.route('/work/update_state', methods=['POST'])
@login_required
def update_state():
    my_message = None
    work = None
    try:
        work_id = request.form.get('work_id')
        work = Work.query.filter_by(id=work_id).first()
        work.state = not work.state
        with lock:
            if work.state:
                create_model(work)
            else:
                delete_model(work)
        db.session.commit()
        add_log(current_user.id, "State of {} = {}".format(work.name, work.state), request.remote_addr)
    except Exception as e:
        if work:
            work.state = False
            db.session.commit()
            add_log(current_user.id, "Exception {} with job {}".format(str(e), work.name), request.remote_addr)
        else:
            add_log(current_user.id, "Exception {}".format(str(e)), request.remote_addr)
        my_message = str(e)
    finally:
        return url_for('main.index', my_message=my_message)


@main.route('/workers/upload_worker', methods=['POST'])
@login_required
def upload_worker():
    try:
        model_type = request.form.get('type').lower()
        name = request.form.get('name')
        model_file = request.files['model_file']
        dep_file = None
        if request.files['requirements']:
            dep_file = request.files['requirements']
        date = datetime.datetime.now().replace(microsecond=0)

        folder_path = ''.join('_' if c in ' .:,/' else c for c in str(date))

        if not os.path.exists(os.path.join(app.instance_path, folder_path)):
            os.makedirs(os.path.join(app.instance_path, folder_path))

        model_file_path = os.path.join(app.instance_path, folder_path, model_file.filename)
        model_file.save(model_file_path)

        if dep_file:
            pip_file_path = os.path.join(app.instance_path, folder_path, dep_file.filename)
            dep_file.save(pip_file_path)
        else:
            pip_file_path = '-'
        worker = Worker(name=name, type=model_type, date=date, worker_path=model_file_path, pip_path=pip_file_path)
        db.session.add(worker)
        db.session.commit()
        add_log(current_user.id, "Upload worker {}".format(worker.name), request.remote_addr)
    except Exception as e:
        flash(str(e))
    finally:
        return redirect(url_for('main.workers'))


@main.route('/tokens/upload_token', methods=['POST'])
@login_required
def upload_token():
    try:
        name = request.form.get('name')
        token_mean = request.form.get('token')
        date = datetime.datetime.now().replace(microsecond=0)
        token = Token(name=name, first=token_mean[:4], token_hash=generate_password_hash(token_mean), date=date)
        db.session.add(token)
        db.session.commit()
        add_log(current_user.id, "Upload token {}".format(token.name), request.remote_addr)
    except Exception as e:
        flash(str(e))
    finally:
        return redirect(url_for('main.tokens'))


@main.route('/works/delete_work', methods=['POST'])
@login_required
def delete_work():
    try:
        delete_id = request.form.get('id')
        deleting_work = Work.query.filter_by(id=delete_id).first()
        db.session.delete(deleting_work)
        db.session.commit()
        add_log(current_user.id, "Delete job {}".format(deleting_work.name), request.remote_addr)
    except Exception as e:
        flash(str(e))
    finally:
        return redirect(url_for('main.index'))


@main.route('/workers/delete_worker', methods=['POST'])
@login_required
def delete_worker():
    try:
        delete_id = request.form.get('id')
        deleting_worker = Worker.query.filter_by(id=delete_id).first()
        if deleting_worker.works:
            flash('Please, delete works with worker {} before'.format(deleting_worker.name))
            return redirect(url_for('main.workers', worker_id=delete_id))
        try:
            folder_path = ''.join('_' if c in ' .:,/' else c for c in str(deleting_worker.date))
            with lock:
                shutil.rmtree(os.path.join(app.instance_path, folder_path))
        except Exception as e:
            flash(str(e))
        db.session.delete(deleting_worker)
        db.session.commit()
        add_log(current_user.id, "Delete worker {}".format(deleting_worker.name), request.remote_addr)
        return redirect(url_for('main.workers'))
    except Exception as e:
        flash(str(e))
        return redirect(url_for('main.workers'))


@main.route('/tokens/delete_token', methods=['POST'])
@login_required
def delete_token():
    try:
        delete_id = request.form.get('id')
        deleting_token = Token.query.filter_by(id=delete_id).first()
        db.session.delete(deleting_token)
        db.session.commit()
        add_log(current_user.id, "Delete token {}".format(deleting_token.name), request.remote_addr)
    except Exception as e:
        flash(str(e))
    finally:
        return redirect(url_for('main.tokens'))


@main.route('/download_stats')
@login_required
def download_stats():
    try:
        work_id = int(request.args.get('work_id'))
        path = os.path.join(app_dir, 'logs', f'work-{work_id}.txt')
        if not os.path.exists(path):
            with lock:
                with open(path, "a") as file:
                    res = Statistics.query.filter_by(work_id=work_id).order_by(asc(Statistics.id)).all()
                    for stat in res:
                        file.write(
                            "Date {}; Work={}; cpu={}; ram={}; gpu={}; time={}; dtw={}; res={}\n".format(stat.date,
                                                                                                         stat.work.name,
                                                                                                         stat.cpu,
                                                                                                         stat.ram,
                                                                                                         stat.gpu,
                                                                                                         stat.time,
                                                                                                         stat.dtw,
                                                                                                         json.loads(
                                                                                                             stat.res)))
        work = Work.query.filter_by(id=work_id).first()
        add_log(current_user.id, "Download stats for job {}".format(work.name), request.remote_addr)
        return send_file(path, mimetype='text/csv', download_name=f'work-{work_id}.txt', as_attachment=True)
    except Exception as e:
        flash(str(e))
        return redirect(url_for('main.index'))


@main.route('/get_user_lvl')
def get_user_lvl():
    try:
        token = request.headers.get('Authorization')
        tokens_list = Token.query.filter_by(first=token[:4]).all()
        for t in tokens_list:
            if check_password_hash(t.token_hash, token):
                if 'lang' in request.args:
                    lang = request.args.get("lang")
                else:
                    lang = 'en'
                dtw = request.args.get("dtw")
                lvl, msg = get_lvl(lang, dtw)
                return jsonify(
                    message=msg,
                    lvl=lvl
                )
        abort(401, description="Access denied")
    except Exception as e:
        return jsonify(
            message=str(e),
            lvl=""
        )
