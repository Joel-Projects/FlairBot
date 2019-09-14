import prawcore, re
from functools import wraps
from flask import session, url_for, redirect, flash, request, abort
from flask_login import current_user

from . import reddit
from .models import *

def validateSubreddit(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            sub = reddit.subreddit(kwargs['subreddit'])
            sub._fetch()
            subreddit = sub.display_name
        except prawcore.exceptions.Redirect:
            subreddit = kwargs['subreddit']
        kwargs['subreddit'] = subreddit
        return func(*args, **kwargs)
    return decorated

def validateSubredditForm(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if request.form['subreddit'] == session['subreddit']:
            try:
                sub = reddit.subreddit(request.form['subreddit'])
                sub._fetch()
                subreddit = sub.display_name
            except prawcore.exceptions.Redirect:
                subreddit = None
                flash(f"That subreddit doesn't exist.")
            kwargs['subreddit'] = subreddit
        else:
            abort(409)
        return func(*args, **kwargs)
    return decorated

def validateUser(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            user = User.query.filter(User.username.ilike(kwargs['user'])).first()
            username = user.username
        except AttributeError:
            username = kwargs['user']
        kwargs['user'] = username
        return func(*args, **kwargs)
    return decorated

def validateUsername(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            username = request.form.get('username')
            if not 3 <= len(username) <= 22:
                kwargs['reason'] = 'Username must be between 3 and 22 characters'
            elif not re.match(r'^[\w-]+$', username):
                kwargs['reason'] = 'Letters, numbers, dashes, and underscores only. Please try again without symbols.'
            else:
                kwargs['username'] = username
        except Exception as reason:
            kwargs['reason'] = reason
        return func(*args, **kwargs)
    return decorated

def validateUserForm(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if request.form['username'] == session['username']:
            try:
                user = User.query.filter(User.username.ilike(request.form['username'])).first()
                username = user.username
            except AttributeError:
                username = request.form['username']
            kwargs['user'] = username
        else:
            abort(409)
        return func(*args, **kwargs)

    return decorated

def requiresAdmin(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if current_user and not current_user.admin:
            abort(403)
        return func(*args, **kwargs)
    return decorated