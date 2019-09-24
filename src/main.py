import os
from flask import Flask, url_for, redirect
from app.hs_oauth.controller import hs_oauth
from app.goog_oauth.controller import goog_oauth
from app.doc_ext.controller import doc_ext

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

app.register_blueprint(hs_oauth)
app.register_blueprint(goog_oauth)
app.register_blueprint(doc_ext)


@app.route('/')
def main_app():
    return redirect(url_for('doc_ext.main_app'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
