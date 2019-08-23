# Copyright (C) jackson1442 - All Rights Reserved
# Unauthorized copying of this file via any medium is strictly prohibited
# Proprietary and confidential
# Written by jackson1442 <me@j1442.co>, July 2019

from flask import Flask, session, redirect, request, url_for, render_template, Response, jsonify, Markup, flash, g
from functools import wraps
import psycopg2, praw, sys
from sentry_sdk.integrations.flask import FlaskIntegration
from BotUtils.CommonUtils import BotServices
from FlairBotMgmt import app
from FlairBotMgmt.decorators_special import *
from FlairBotMgmt.basicutils import *

# sentry_sdk.init(dsn="https://9704c3e2823044ae9f9b5db73d03dac9@sentry.jkpayne.com/21", integrations=[FlaskIntegration()])
services = BotServices('FlairBot')
sql = services.postgres()

@app.route('/')
def home():
    redditauth = praw.Reddit(client_id=get_secret('reddit_web', 'client_id'), client_secret=get_secret('reddit_web', 'client_secret'), user_agent='Authentication handler for JES Flair v0, web', redirect_uri='https://flair.jesassn.org/authenticate')
    url = redditauth.auth.url(['identity', 'modflair', 'mysubreddits'], 'cheese')
    return render_template('home.html', url=url)

@app.route('/dash')
@requires_auth
def dash():
    return render_template('dash.html')\

@app.route('/nav')
def nav():
    return render_template('nav.html')

@app.route('/subreddits')
def subreddits():
    sql.execute('SELECT * FROM flairbots.subreddits')
    subreddits = sql.fetchall()
    sql.execute('SELECT * FROM flairbots.removal_reasons')
    removalReasons = sql.fetchall()
    reasonCounts = {}
    for reason in removalReasons:
        if not reason.subreddit in reasonCounts:
            reasonCounts[reason.subreddit] = 0
        reasonCounts[reason.subreddit] += 1
    return render_template('subreddits.html', subreddits=subreddits, reasonCounts=reasonCounts)

@app.route('/api/subreddit/enable', methods=['POST'])
def toggleSubreddit():
    subreddit = request.form['subreddit']
    enabled = bool(request.form['enabled'])
    sql.execute('UPDATE flairbots.subreddits SET enabled = not enabled WHERE subreddit=%s',  (subreddit,))
    sql.execute('SELECT * FROM flairbots.subreddits where subreddit=%s', (subreddit,))
    subreddit = sql.fetchone()
    sql.execute('SELECT * FROM flairbots.removal_reasons')
    removalReasons = sql.fetchall()
    reasonCounts = {}
    for reason in removalReasons:
        if not reason.subreddit in reasonCounts:
            reasonCounts[reason.subreddit] = 0
        reasonCounts[reason.subreddit] += 1
    # return render_template('subreddits.html', subreddits=subreddits, reasonCounts=reasonCounts)
    return jsonify({'status': 'success', 'subreddit': subreddit.subreddit, 'enabled': subreddit.enabled})

@app.route('/subreddits/<subreddit>')
def editSubreddit(subreddit):
    # reddit = services.reddit('Lil_SpazJoekp')
    # rsubreddit = reddit.subreddit(subreddit)
    # rsubreddit._fetch()
    # subreddit = rsubreddit.display_name
    sql.execute('SELECT * FROM flairbots.subreddits WHERE subreddit=%s', (subreddit,))
    subreddit = sql.fetchone()
    return render_template('edit_subreddit.html', subreddit = subreddit)

