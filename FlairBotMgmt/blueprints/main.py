import praw
from flask import Blueprint, render_template
from flask_login import login_required
from . import *

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def root():
    return render_template('dash.html')

@main.route('/dash')
@login_required
def dash():
    return render_template('dash.html')

@main.route('/users')
@login_required
@requiresAdmin
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@main.route('/profile')
@login_required
def profile():
    return render_template('edit_user.html', user=current_user)