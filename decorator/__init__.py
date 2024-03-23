from functools import wraps


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
