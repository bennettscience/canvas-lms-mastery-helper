from flask import redirect, url_for
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


class AuthorizedAdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.usertype_id == 1
    
    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('home_bp.index'))


class AdminView(ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_folder = 'static'
    
    def is_accessible(self):
        print(current_user.usertype_id)
        if current_user.usertype_id == 1:
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('home_bp.index'))

class UserView(AdminView):
    column_list = ('user_type', 'canvas_id', 'name')
    column_sortable_list = ('user_type', ('user_type', 'user_type.name'), 'name')
    column_searchable_list = ['name']
    column_filters = ['user_type']
