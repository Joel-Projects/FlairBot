import re, requests
from functools import wraps
from flask import session, url_for, redirect, flash, request, abort
from flask_login import current_user
from .models import *

def validateSub(subreddit):
    try:
        response = requests.get(f"https://reddit.com/r/{subreddit}/about.json", headers={'user-agent': 'python:com.jkpayne.redditapps/FlairBot by /u/Lil_SpazJoekp'})
        while response.status_code not in (200, 403):
            response = requests.get(f"https://reddit.com/r/{subreddit}/about.json", headers={'user-agent': 'python:com.jkpayne.redditapps/FlairBot by /u/Lil_SpazJoekp'})
        subreddit = response.json()['data']['display_name']
    except KeyError:
        return None
    return subreddit

def validateRedditor(redditor):
    try:
        response = requests.get(f"https://reddit.com/user/{redditor}/about.json", headers={'user-agent': 'python:com.jkpayne.redditapps/FlairBot by /u/Lil_SpazJoekp'})
        while response.status_code not in (200, 403, 404):
            response = requests.get(f"https://reddit.com/user/{redditor}/about.json", headers={'user-agent': 'python:com.jkpayne.redditapps/FlairBot by /u/Lil_SpazJoekp'})
        redditor = response.json()['data']['name']
    except KeyError:
        return None
    return redditor

def validateBotAccount(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if 'bot_account' in request.form:
            botAccountKey = 'bot_account'
        else:
            botAccountKey = 'botAccount'
        bot_account = validateRedditor(request.form[botAccountKey])
        kwargs['bot_account'] = bot_account
        return func(*args, **kwargs)
    return decorated

def validateSubreddit(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if 'subreddit' in kwargs:
            subreddit = validateSub(kwargs['subreddit'])
        else:
            subreddit = validateSub(request.form['subreddit'])
        kwargs['subreddit'] = subreddit
        return func(*args, **kwargs)
    return decorated

def validateSubredditForm(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if request.form['subreddit'] == session['subreddit']:
            subreddit = validateSub(kwargs['subreddit'])
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