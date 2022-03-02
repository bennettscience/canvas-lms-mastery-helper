from flask import session, redirect, url_for, request
from flask_admin.contrib.sqla import ModelView

class AdminView(ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_folder = 'static'
    
    def is_accessible(self):
        return session.get('user.usertype_id') == 1

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('home', next=request.url))

class UserView(ModelView):
    column_list = ('user_type', 'canvas_id', 'name')
    column_sortable_list = ('user_type', ('user_type', 'user_type.name'), 'name')
    column_searchable_list = ['name']
    column_filters = ['user_type']