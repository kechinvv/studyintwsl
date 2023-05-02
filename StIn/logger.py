import datetime
import os

from sqlalchemy import asc

from StIn import db, lock
from StIn.models import UserLog
from StIn.works_handler import app_dir


def add_log(current_user_id, msg, addr):
    path = os.path.join(app_dir, 'logs', f'user-{current_user_id}.txt')
    if os.path.exists(path):
        with lock:
            os.remove(path)
    row = UserLog(user_id=current_user_id, action=msg, addr=addr, date=datetime.datetime.now().replace(microsecond=0))
    db.session.add(row)
    db.session.commit()
    rows = UserLog.query.filter_by(user_id=current_user_id).count()
    if rows > 10000:
        deleting_row = UserLog.query.filter_by(user_id=current_user_id).order_by(asc(UserLog.id)).first()
        db.session.delete(deleting_row)
        db.session.commit()
