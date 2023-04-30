from functools import wraps

from flask import Blueprint, render_template_string, flash
from flask import redirect, url_for
from flask_login import current_user, login_required

from StIn.models import ACCESS

admin = Blueprint('admin', __name__)


def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:  # the user is not logged in
                return redirect(url_for('auth.login'))

            # user = User.query.filter_by(id=current_user.id).first()

            if not current_user.allowed(access_level):
                flash('You do not have access to this resource.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@admin.route("/owner_panel")
@login_required
@requires_access_level(ACCESS['owner'])
def member_control():
    return render_template_string('<h1>owner</h1> <a href="/">Go back?</a>')


@admin.route("/senior_panel")
@login_required
@requires_access_level(ACCESS['senior'])
def junior_control():
    return render_template_string('<h1>senior</h1> <a href="/">Go back?</a>')