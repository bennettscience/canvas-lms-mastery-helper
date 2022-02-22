import time
from flask import request, session
from canvasapi import Canvas
from requests_oauthlib import OAuth2Session

from app import app

class CanvasAuthService:
    """ Handle authentication through Canvas OAuth. Fall back to scoped
    API token if the OAuth object isn't present (ie, during automated tasks). """

    # Define application scopes to send with the authorization request
    scope_list = [
        "url:GET|/api/v1/courses",
        "url:GET|/api/v1/courses/:id",
        "url:GET|/api/v1/users/:user_id/courses",
        "url:GET|/api/v1/courses/:course_id/assignments",
        "url:GET|/api/v1/courses/:course_id/assignments/:id",
        "url:GET|/api/v1/courses/:course_id/enrollments",
        "url:GET|/api/v1/courses/:course_id/outcome_group_links",
        "url:GET|/api/v1/courses/:course_id/outcome_results",
        "url:GET|/api/v1/outcomes/:id",
        "url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/submissions",
        "url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id",
        "url:PUT|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id"
    ]

    scope = " ".join(scope_list)

    if app.config['CANVAS_OAUTH']:
        oauth = OAuth2Session(
            client_id=app.config['CANVAS_OAUTH']['id'],
            redirect_uri=app.config['CANVAS_OAUTH']['redirect_url'],
            scope=scope
        )

    def init_canvas(self):
        if session['_fresh'] and app.config['CANVAS_OAUTH']:

            expire = session['oauth_token']['expires_at']

            # The current token has expired, so get a new one from the OAuth endpoint
            if time.time() > expire:
                client_id = app.config['CANVAS_OAUTH']['id']
                refresh_url = app.config['CANVAS_OAUTH']['token_url']

                params = {
                    "client_id": client_id,
                    "client_secret": app.config['CANVAS_OAUTH']['secret'],
                    "refresh_token": session['oauth_token']['refresh_token']
                }

                # Don't use the self property because you can go right
                # to the token endpoint without logging back in.
                oauth_refresh = OAuth2Session(client_id, token=session['oauth_token'])

                # Set the current session token to the new value
                session['oauth_token'] = oauth_refresh.refresh_token(refresh_url, **params)

            # canvaspi throws an error if you include the /api/v1 suffix. Pass in
            # a short URL to instantiate.
            return Canvas(app.config['CANVAS_OAUTH']['base_url_short'], session['oauth_token']['access_token'])
        else:
            return Canvas(app.config['CANVAS_URI'], app.config['CANVAS_KEY'])

    def login(self):
        return self.oauth.authorization_url(app.config['CANVAS_OAUTH']['authorization_url'])
    
    def get_token(self):
        # Override request.url with an HTTPS protocol because it defaults
        # to http: for some reason and throws an InsecureTransportError.
        # seehttps://github.com/requests/requests-oauthlib/issues/287#issuecomment-640804112
        temp_url = request.url
        if "http:" in temp_url:
            temp_url = "https:" + temp_url[5:]

        token = self.oauth.fetch_token(
            app.config['CANVAS_OAUTH']['token_url'],
            client_secret=app.config['CANVAS_OAUTH']['secret'],
            authorization_response=temp_url,
            state=session['oauth_state'],
            replace_tokens=True
        )
        return token