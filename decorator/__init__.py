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


# redirect to worker profile if worker logged in
def redirect_to_worker_profile(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_worker:
            return redirect(url_for("worker.home"))
        return f(*args, **kwargs)
    return decorated_function


# must not be logged in
def check_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.is_worker and not current_user.worker_profile:
                return redirect(url_for("worker.update_profile"))
            return redirect(url_for("user.home"))
        return f(*args, **kwargs)
    return decorated_function


# check not logged in
def check_not_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("user.home"))
        return f(*args, **kwargs)
    return decorated_function
