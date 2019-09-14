import praw
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from .. import reddit
from . import *

users = Blueprint('users', __name__, url_prefix='/u')

@users.route('/<user>', methods=['GET'])
@login_required
@requiresAdmin
def viewUser(user):
    username = user
    session['username'] = user
    user = User.query.filter_by(username=username).first()
    notification = {'success': None, 'error': None}
    if user:
        return render_template('edit_user.html', user=user, notification=notification), 202
    return render_template('errors/404.html'), 404


@users.route('/new', methods=['GET', 'POST'])
@login_required
@requiresAdmin
def newRemovalReason():
    removalReason = None
    notification = None
    subreddits = Subreddit.query.all()
    return render_template('edit_removal_reason.html', removalReason=removalReason, notification=notification, subreddits=subreddits), 202