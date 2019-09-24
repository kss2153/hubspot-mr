from flask import Blueprint, request, redirect, session, url_for
from app.util import get_home
import google.oauth2.credentials
import google_auth_oauthlib.flow

SCOPES = [
    'https://www.googleapis.com/auth/documents.readonly',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

goog_oauth = Blueprint('goog_oauth', __name__, url_prefix='/auth/goog')


"""
google oauth2 endpoints
"""
@goog_oauth.route('/authorize')
def authorize_goog():
    session['goog_home'] = get_home()
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('credentials.json', SCOPES)
    flow.redirect_uri = url_for('.goog_redirect', _external=True)
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['goog_code_verifier'] = flow.code_verifier
    session['good_oauth_state'] = state
    return redirect(authorization_url)


@goog_oauth.route('/redirect')
def goog_redirect():
    state = session['good_oauth_state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('credentials.json', scopes=SCOPES, state=state)
    flow.code_verifier = session.get('goog_code_verifier')
    flow.redirect_uri = url_for('.goog_redirect', _external=True)
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    session['goog_credentials'] = credentials_to_dict(credentials)
    home = session.get('goog_home')
    session.pop('goog_home', None)
    return redirect(url_for(home))


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
