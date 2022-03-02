from functools import wraps
from flask import abort, g, redirect, request, url_for
from flask_login import current_user


def restricted():
    def _restricted(func):
        @wraps(func)
        def __restricted(*args, **kwargs):
            if current_user.is_anonymous:
                return redirect(url_for('home_bp.index', next=request.url))
            else:
                # Redirect students away from restricted endpoints
                if current_user.usertype_id == 3:
                    return abort(401, "You do not have permission to view this page.")
                return func(*args, **kwargs)
        return __restricted
    return _restricted