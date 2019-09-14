import praw
from flask import Blueprint, render_template, redirect
from flask_login import current_user, login_required
from . import *

main = Blueprint('main', __name__)

@main.route('/')
def root():
    if current_user.is_authenticated:
        return render_template('dash.html')
    else:
        return redirect('/login')

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