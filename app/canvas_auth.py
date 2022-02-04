import time
from flask import request, session
from canvasapi import Canvas
from requests_oauthlib import OAuth2Session

from app import app

class CanvasAuthService:
    """ Handle authentication through Canvas OAuth """

    oauth = OAuth2Session(
        app.config['CANVAS_OAUTH']['id'],
        redirect_uri=app.config['CANVAS_OAUTH']['redirect_url']
    )

    auth_url = oauth.authorization_url(
        app.config['CANVAS_OAUTH']['authorization_url']
    )

    def init_canvas(self):
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

    def login(self):
        return self.auth_url
    
    def get_token(self):
        token = self.oauth.fetch_token(
            app.config['CANVAS_OAUTH']['token_url'],
            client_secret=app.config['CANVAS_OAUTH']['secret'],
            authorization_response=request.url,
            state=session['oauth_state'],
            replace_tokens=True
        )
        return token