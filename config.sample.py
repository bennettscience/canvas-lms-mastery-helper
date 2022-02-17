import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # Define the flask environment. Defaults to 'production'
    FLASK_ENV = 'development'
    # Disable secure HTTPS requirement locally. Set to 0 (or remove)
    # while in production.
    # see https://oauthlib.readthedocs.io/en/latest/oauth2/security.html#envvar-OAUTHLIB_INSECURE_TRANSPORT
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "someSuperSecret"

    CANVAS_URI = os.environ.get('CANVAS_URI')
    CANVAS_KEY = os.environ.get('CANVAS_KEY')

    # Set your OAuth parameters in your environment file or
    # overwrite each key below with your Canvas information.
    CANVAS_OAUTH = {
        'id': os.environ.get('CANVAS_OAUTH_APP_ID'),
        'secret': os.environ.get('CANVAS_OAUTH_APP_SECRET'),
        'base_url_short': os.environ.get('CANVAS_URI'),
        'base_url': os.environ.get('CANVAS_URI') + 'api/v1/',
        'token_url': os.environ.get('CANVAS_URI') + 'login/oauth2/token',
        'authorization_url': os.environ.get('CANVAS_URI') + 'login/oauth2/auth',
        'redirect_url': os.environ.get('CANVAS_OAUTH_CALLBACK_URI'),
    }