from flask import request, url_for, session
from app.db import SqlSession


def get_home():
    home = 'main_app'
    home_arg = request.args.get('home')
    if home_arg:
        try:
            url_for(home_arg)
        except:
            print('%s is an invalid route. Defaulting to main_app.' % home_arg)
            return home
        home = request.args.get('home')
    return home


def pop_messages():
    msg_red = session.get('msg_red')
    msg_green = session.get('msg_green')
    session.pop('msg_red', None)
    session.pop('msg_green', None)
    return msg_red, msg_green
