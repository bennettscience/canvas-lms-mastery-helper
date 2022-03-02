from flask import abort, redirect
from flask_login import current_user


def teacher_required(func):
    def check_is_teacher(*args, **kwargs):
        if current_user.is_anonymous:
            return redirect('/')
        else:
            if current_user.user_type != "Teacher":
                return abort(401, "You do not have permission to view this page.")
            return func(*args, **kwargs)
    return check_is_teacher()