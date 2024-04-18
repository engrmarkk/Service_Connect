from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, abort


def worker_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_worker:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorated_function


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_worker is False:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorated_function


# complete profile
def complete_profile(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.is_worker and not current_user.worker_profile:
                return redirect(url_for("worker.update_profile"))
            return f(*args, **kwargs)
        else:
            return f(*args, **kwargs)
    return decorated_function
