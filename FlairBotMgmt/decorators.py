import prawcore
from functools import wraps
from flask import session, url_for, redirect, flash, request, abort
from flask_login import current_user

from . import reddit

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

def requiresAdmin(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if current_user and current_user.admin:
            flash("You're not allowed to do that")
        return func(*args, **kwargs)
    return decorated