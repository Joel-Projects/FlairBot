import praw
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from flask_login import login_required, current_user
from . import *

users = Blueprint('users', __name__, url_prefix='/u')

@users.route('/<user>', methods=['GET'])
@login_required
def viewUser(user):
    username = user
    session['username'] = user
    user = User.query.filter_by(username=username).first()
    notification = {'success': None, 'error': None}
    if user:
        if current_user.admin or current_user == user:
            return render_template('edit_user.html', user=user, notification=notification), 200
        else:
            return render_template('errors/403.html', message="You're not allowed to view this page"), 403
    return render_template('errors/404.html'), 404
