from flask import Blueprint, request, redirect, session, url_for, render_template, jsonify
from googleapiclient.discovery import build
import google.oauth2.credentials as g_cred
from app.hs_oauth.controller import get_token_info
from app.goog_oauth.controller import credentials_to_dict
from app.util import pop_messages
from app.db import SqlSession
from .model import Template

COMPANY_PARAMS = ['name', 'address', 'address2', 'city', 'state', 'zip', 'country', 'phone', 'domain', 'website']
CONTACT_PARAMS = ['firstname', 'lastname', 'city', 'state', 'zip', 'address', 'country', 'company', 'email', 'phone']

doc_ext = Blueprint('doc_ext', __name__, url_prefix='/docs')


"""
entrypoint of app
"""
@doc_ext.route('/', methods=["GET"])
def main_app():
    # save params sent from hubspot to session (if any)
    if len(request.args.to_dict()) > 0:
        session['crm_params'] = request.args.to_dict()

    # check for hubspot and google authentication
    if not session.get("hs_oauth_token"):
        return redirect(url_for('hs_oauth.authorize_hub', hs_home='doc_ext.main_app'))
    label = 'CREATE DOC'
    if not session.get('goog_credentials'):
      label = 'SIGN INTO GOOGLE'

    # get hub id for logged in user's account
    token_info = get_token_info()
    session['hub_id'] = str(token_info['hub_id'])

    templates = get_templates()
    show = session.get('crm_params') is not None and len(templates) > 0
    msg_red, msg_green = pop_messages()
    return render_template('doc_ext/main.html', label=label, templates=templates, msg_green=msg_green, msg_red=msg_red, show=show)


@doc_ext.route('/', methods=['POST'])
def main_app_post():
    file_id = request.form.get('template')
    return redirect(url_for('doc_ext.create_doc', file_id=file_id))


@doc_ext.route('/add_template', methods=['POST'])
def add_template():
    object_type = request.form.get('objectType')
    name = request.form['templateName']
    hub_id = session.get('hub_id')
    file_id = request.form['fileId']
    if name == '' or file_id == '':
        session['msg_red'] = 'fill all template fields'
        return redirect(url_for('doc_ext.main_app'))

    s = SqlSession()
    q = s.query(Template).filter_by(hub_id=hub_id, template_name=name, associated_object=object_type)
    if q.first() is not None:
        session['msg_red'] = 'choose a new name for your template'
    else:
        s.add(Template(hub_id=hub_id, template_id=file_id, template_name=name, associated_object=object_type))
        s.commit()
        session['msg_green'] = 'successfully added template'
    return redirect(url_for('doc_ext.main_app'))


"""
create doc action
"""
@doc_ext.route('/create_doc')
def create_doc():
    if not session.get('goog_credentials'):
        return redirect(url_for('goog_oauth.authorize_goog'))

    file_id = request.args.get('file_id')
    if file_id is None:
        session['msg_red'] = 'no file id given'
        return redirect(url_for('.main_app'))

    credentials = g_cred.Credentials(**session['goog_credentials'])
    session['goog_credentials'] = credentials_to_dict(credentials)
    try:
        drive_service = build('drive', 'v3', credentials=credentials)
        drive_response = drive_service.files().copy(fileId=file_id).execute()
        document_copy_id = drive_response.get('id')
    except:
        session['msg_red'] = 'failed to copy template'
        return redirect(url_for('.main_app'))

    try:
        service = build('docs', 'v1', credentials=credentials)
        params = get_params()
        requests = list(map(lambda x: get_replace_request(x), params))
        if len(requests) > 0:
            service.documents().batchUpdate(documentId=document_copy_id, body={'requests': requests}).execute()
    except:
        session['msg_red'] = 'failed to replace variables'
        return redirect(url_for('.main_app'))

    session.pop('crm_params', None)
    session['msg_green'] = 'successfully created doc'
    return redirect(url_for('.main_app'))


"""
fetch card info
"""
@doc_ext.route('/api/crm_card')
def crm_card():
    given_uri = request.url
    split = given_uri.split('?', 1)
    if len(split) > 1:
        params = split[1]
    else:
        params = ''
    link = 'https://hubspot-mr.appspot.com/docs?%s' % params
    resp = {
        "results": [
            {
                "objectId": 245,
                "title": "DOC EXTENSION",
                "link": link
            }
        ]
    }
    return jsonify(resp)


def get_params():
    if not session.get('crm_params'):
        return []
    object_type = session.get('crm_params')['associatedObjectType']
    if object_type == 'COMPANY':
        return COMPANY_PARAMS
    elif object_type == 'CONTACT':
        return CONTACT_PARAMS
    else:
        return []


def get_replace_request(param):
    return {
        'replaceAllText': {
            'containsText': {
                'text': '{{%s}}' % param,
                'matchCase':  'true'
            },
            'replaceText': get_variable(param)
        }
    }


def get_variable(param):
    params = session.get('crm_params')
    if (params is None):
        params = {}
    if param in params:
        return params[param]
    return ''


def get_templates():
    s = SqlSession()
    if session.get('hub_id') and session.get('crm_params'):
        object_type = session.get('crm_params')['associatedObjectType']
        q = s.query(Template).filter_by(hub_id=session.get('hub_id'), associated_object=object_type)
        return q.all()
    return []
