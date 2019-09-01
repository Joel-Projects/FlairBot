import praw, sentry_sdk, prawcore, psycopg2
from flask import Flask, session, redirect, request, url_for, render_template, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from sentry_sdk.integrations.flask import FlaskIntegration
from BotUtils.CommonUtils import BotServices


conn = services.postgres(flask=True)
conn.autocommit = True

def requiresLogin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html', message=error), 404
