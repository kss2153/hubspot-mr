import os
from flask import Blueprint, request, redirect, session, url_for
from app.util import get_home
from oauthlib.oauth2 import MissingTokenError
from requests_oauthlib import OAuth2Session

if os.environ.get('GAE_ENV') != 'standard':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

hub_scope = ['oauth', 'contacts']
client_id = os.environ.get('HUBSPOT_CLIENT_ID')
client_secret = os.environ.get('HUBSPOT_CLIENT_SECRET')

token_url = 'https://api.hubapi.com/oauth/v1/token'
authorization_base_url = 'https://app.hubspot.com/oauth/authorize'

hs_oauth = Blueprint('hs_oauth', __name__, url_prefix='/auth/hs')

"""
hubspot oauth2 endpoints
"""
@hs_oauth.route('/authorize')
def authorize_hub():
    session['hs_home'] = get_home()
    if session.get("hs_oauth_token"):
        return redirect(url_for(session.get('hs_home')))
    redirect_uri = url_for('.hub_redirect', _external=True)
    hubspot = OAuth2Session(client_id, scope=hub_scope, redirect_uri=redirect_uri)
    authorization_url, state = hubspot.authorization_url(authorization_base_url)
    session['hs_oauth_state'] = state
    return redirect(authorization_url)


@hs_oauth.route("/redirect", methods=["GET"])
def hub_redirect():
    code = request.values.get('code')
    redirect_uri = url_for('.hub_redirect', _external=True)
    hubspot = OAuth2Session(client_id, state=session['hs_oauth_state'])
    token = hubspot.fetch_token(token_url, method='POST',
                                client_secret=client_secret,
                                authorization_response=request.url,
                                body="grant_type=authorization_code&client_id=" + client_id + "&client_secret=" + client_secret + "&redirect_uri=" + redirect_uri + "&code=" + code)
    session['hs_oauth_token'] = token
    home = session.get('hs_home')
    session.pop('hs_home', None)
    return redirect(url_for(home))


def get_token_info():
    if session.get("hs_oauth_token"):
        refresh_token = session["hs_oauth_token"].get("refresh_token")
        token_info_url = 'https://api.hubapi.com/oauth/v1/refresh-tokens/%s' % refresh_token
        hubspot = OAuth2Session(client_id, state=session['hs_oauth_state'])
        data = hubspot.get(token_info_url)
        return data.json()
    else:
        return None
