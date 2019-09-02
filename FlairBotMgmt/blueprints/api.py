import praw
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from . import *

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/subreddit/toggle', methods=['POST'])
@login_required
@requiresAdmin
def toggleSubreddit():
    subreddit = request.form['subreddit']
    notification = {'success': None, 'error': None}
    try:
        subreddit = Subreddit.query.filter_by(subreddit=subreddit).first()
        subreddit.enabled = not subreddit.enabled
        db.session.merge(subreddit)
        db.session.commit()
        notification['success'] = True
    except Exception as error:
        notification['error'] = error
    return jsonify({'success': notification['success'], 'error': notification['error'], 'subreddit': subreddit.subreddit, 'enabled': subreddit.enabled}), 202

@api.route('/subreddit/delete', methods=['POST'])
@login_required
@requiresAdmin
@validateSubredditForm
def deleteSubreddit(subreddit=None):
    notification = {'success': None, 'error': None}
    subname = subreddit
    try:
        subreddit = Subreddit.query.filter_by(subreddit=subreddit).first()
        if subreddit:
            db.session.delete(subreddit)
            db.session.commit()
            notification['success'] = True
        else:
            notification['error'] = "That subreddit doesn't exist"
    except Exception as error:
        notification['error'] = error
    return jsonify({'success': notification['success'], 'error': notification['error'], 'notification': notification, 'subreddit': subname}), 202

@api.route('/subreddit/edit', methods=['POST'])
@login_required
@requiresAdmin
@validateSubredditForm
def editSubreddit(subreddit=None):
    bot_account = request.form['botAccount']
    webhook_type = request.form['webhookType']
    webhook = request.form['webhook']
    if not webhook:
        webhook_type = None
    headerToggle = request.form.get('headerToggle')
    footerToggle = request.form.get('footerToggle')
    header = request.form['headerText']
    footer = request.form['footerText']
    if not headerToggle:
        header = None
    if not footerToggle:
        footer = None
    subreddit = Subreddit.query.filter_by(subreddit=subreddit).first()
    notification = {'success': None, 'error': None}
    try:
        if subreddit:
            subreddit.bot_account = bot_account
            subreddit.webhook_type = webhook_type
            subreddit.webhook = webhook
            subreddit.header = header
            subreddit.footer = footer
            db.session.merge(subreddit)
            subredditEditType = 'Updated'
        else:
            subreddit = Subreddit(bot_account=bot_account, webhook_type=webhook_type, webhook=webhook, header=header, footer=footer)
            db.session.add(subreddit)
            subredditEditType = 'Added'
        db.session.commit()

        notification['success'] = f'{subredditEditType} r/{subreddit.subreddit} successfully!'
    except Exception as error:
        notification['error'] = error
    return jsonify({'notification': notification, 'subreddit': subreddit.subreddit}), 202

@api.route('/subreddit/add', methods=['POST'])
def addSubreddit():
    subreddit = request.form['subreddit']
    bot_account = request.form['bot_account']
    try:
        sub = reddit.subreddit(subreddit)
        sub._fetch()
        subredditName = sub.display_name
        validSubreddit = True
    except prawcore.Redirect:
        subredditName = None
        validSubreddit = False
    try:
        bot_account = reddit.redditor(bot_account)
        bot_account._fetch()
        bot_account = bot_account.name
        validRedditor = True
    except prawcore.NotFound:
        validRedditor = False
    webhook_type = request.form['webhook_type']
    webhook = request.form['webhook']
    if not webhook:
        webhook_type = None
    headerToggle = request.form.get('headerToggle') == 'true'
    footerToggle = request.form.get('footerToggle') == 'true'
    header = request.form['header']
    footer = request.form['footer']
    enable = request.form.get('enable') == 'true'
    if not headerToggle:
        header = None
    if not footerToggle:
        footer = None
    exitsting = Subreddit.query.filter_by(subreddit=subredditName).first()
    subredditExists = False
    success = None
    error = None
    try:
        if exitsting:
            subredditExists = True
        if validSubreddit and validRedditor and not subredditExists:
            subreddit = Subreddit(subreddit=subredditName, bot_account=bot_account, webhook_type=webhook_type, webhook=webhook, header=header, footer=footer, enabled=enable)
            db.session.add(subreddit)
            subredditEditType = 'Added'
            db.session.commit()
            success = f'{subredditEditType} r/{subreddit.subreddit} successfully!'
    except Exception as er:
        error = er
    if not isinstance(subreddit, str):
        subredditData = {'subreddit': subreddit.subreddit, 'bot_account': subreddit.bot_account, 'webhook_type': subreddit.webhook_type, 'webhook': subreddit.webhook, 'header': subreddit.header, 'footer': subreddit.footer, 'enabled': subreddit.enabled}
    else:
        subredditData = {}
    return jsonify({'success': success, 'error': error, 'subredditExists': subredditExists, 'validSubreddit': validSubreddit, 'validRedditor': validRedditor, 'subreddit':  subredditData}), 202

@api.route('/users/create', methods=['POST'])
@login_required
@requiresAdmin
def createuser():

    username = request.form.get('username')
    password = request.form.get('password')
    admin = True if request.form.get('admin') else False

    success = True
    error = False

    try:
        user = User.query.filter_by(username=username).first()

        if user:
            flash('That user already exists')
        new_user = User(username=username, admin=admin, password=generate_password_hash(password, "pbkdf2:sha256:80000", 80000))

        db.session.add(new_user)
        db.session.commit()
    except Exception as error:
        success = False
        error = error
    return jsonify({'success': success, 'error': error, 'user': User.__dict__,}), 202