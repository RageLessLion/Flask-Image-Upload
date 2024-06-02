from functools import wraps
from flask import abort, session

from database import User


def AdminRequired(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            abort(404)
        user = User.query.filter_by(username=session['username']).first()
        if user is None or not user.is_admin:
            abort(404)
        return f(*args, **kwargs)

    return decorated_function
