import praw
import requests
from flask import Flask, session, redirect, request, url_for, render_template, Response, jsonify, Markup, flash, g
from FlairBotMgmt import app
from FlairBotMgmt.basicutils import *


@app.route('/authenticate')
def authenticate():
    redditauth = praw.Reddit(client_id=get_secret('reddit_web', 'client_id'), client_secret=get_secret('reddit_web', 'client_secret'), user_agent='Authentication handler for JES Flair v0, web', redirect_uri='https://flair.jesassn.org/authenticate')
    session.permanent = True
    state = request.args.get('state')
    if not state:
        return '<pre>401 Authorization Required</pre>', 401
    try:
        token = redditauth.auth.authorize(request.args['code'])
    except:
        return '<pre>401 Authorization Required</pre>', 401
    print(token, request.args['code'])
    username = get_username(token)
    session['username'] = username
    return redirect('/dash')


@app.route('/logout')
def logout():
    [session.pop(k) for k in list(session.keys())]
    return redirect(url_for('home'))


def get_username(token):
    reddit = praw.Reddit(client_id=get_secret('reddit_web', 'client_id'), client_secret=get_secret('reddit_web', 'client_secret'), user_agent='Authentication handler for JES Flair v0, web', refresh_token=token)
    return reddit.user.me().name
