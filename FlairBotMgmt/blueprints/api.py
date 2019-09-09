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
def deleteSubreddit():
    print(f'Deleting Subreddit')
    notification = {'success': None, 'error': None}
    subname = request.form['subreddit']
    deleteRemovalReasons = request.form.get('cascade') == 'true'
    try:
        if deleteRemovalReasons:
            removalReasons = RemovalReason.query.filter_by(subreddit=subname)
            removalReasons.delete()
            db.session.commit()
        subreddit = Subreddit.query.filter_by(subreddit=subname).first()
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
@login_required
@requiresAdmin
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
    except Exception as err:
        error = str(err)
    if not isinstance(subreddit, str):
        subredditData = {'subreddit': subreddit.subreddit, 'bot_account': subreddit.bot_account, 'webhook_type': subreddit.webhook_type, 'webhook': subreddit.webhook, 'header': subreddit.header, 'footer': subreddit.footer, 'enabled': subreddit.enabled}
    else:
        subredditData = {}
    return jsonify({'success': success, 'error': error, 'subredditExists': subredditExists, 'validSubreddit': validSubreddit, 'validRedditor': validRedditor, 'subreddit':  subredditData}), 202

@api.route('/reason/toggle', methods=['POST'])
@login_required
@requiresAdmin
def toggleReason():
    reasonId = request.form['id']
    notification = {'success': None, 'error': None}
    try:
        reason = RemovalReason.query.filter_by(id=reasonId).first()
        reason.enabled = not reason.enabled
        db.session.merge(reason)
        db.session.commit()
        notification['success'] = True
    except Exception as error:
        notification['error'] = error
    return jsonify({'success': notification['success'], 'error': notification['error'], 'id': reasonId, 'enabled': reason.enabled}), 202

@api.route('/reason/delete', methods=['POST'])
@login_required
@requiresAdmin
def deleteReason():
    notification = {'success': None, 'error': None}
    reasonId = request.form['reason_id']
    reason = RemovalReason.query.filter_by(id=reasonId).first()
    try:
        if reason:
            db.session.delete(reason)
            db.session.commit()
            notification['success'] = True
        else:
            notification['error'] = "That reason isn't valid!"
    except Exception as error:
        notification['error'] = error
    return jsonify({'success': notification['success'], 'error': notification['error'], 'notification': notification, 'subreddit': reason.subreddit, 'flair_text': reason.flair_text}), 202

@api.route('/reason/edit', methods=['POST'])
@login_required
@requiresAdmin
def editReason():
    reasonId = request.form['reason_id']
    subreddit = request.form['subreddit']
    flair_text = request.form['flair_text']
    description = request.form['description']
    commentToggle = request.form['commentToggle'] == 'on'
    if commentToggle:
        commentInput = request.form['commentInput']
    else:
        commentInput = None
    lockToggle = request.form['lockToggle'] == 'true'
    commentLockToggle = request.form['commentLockToggle'] == 'on'
    banToggle = request.form['banToggle'] == 'true'
    if banToggle:
        ban_duration = request.form['ban_duration']
        ban_reason = request.form['ban_reason']
        ban_message = request.form['ban_message']
        ban_note = request.form['ban_note']
    else:
        ban_duration = None
        ban_reason = None
        ban_message = None
        ban_note = None
    usernoteToggle = request.form['usernoteToggle'] == 'on'
    if usernoteToggle:
        usernote_note = request.form['usernote_note']
        usernote_warning_type = request.form['usernote_warning_type']
    else:
        usernote_note = None
        usernote_warning_type = None
    reason = RemovalReason.query.filter_by(id=reasonId).first()
    notification = {'success': None, 'error': None}
    try:
        if reason:
            reason.subreddit = subreddit
            reason.flair_text =  flair_text
            reason.description = description
            reason.comment = commentInput
            reason.lock = lockToggle
            reason.lock_comment = commentLockToggle
            reason.ban = banToggle
            reason.ban_duration = ban_duration
            reason.ban_reason =  ban_reason
            reason.ban_message = ban_message
            reason.ban_note = ban_note
            reason.usernote = usernoteToggle
            reason.usernote_note = usernote_note
            reason.usernote_warning_type = usernote_warning_type
            db.session.merge(reason)
            reasonEditType = 'Updated'
        else:
            reason = RemovalReason(subreddit=subreddit, flair_text=flair_text, description=description, comment=commentInput, lock=lockToggle, lock_comment=commentLockToggle, ban=banToggle, ban_duration=ban_duration, ban_reason=ban_reason, ban_message=ban_message, ban_note=ban_note, usernote=usernoteToggle, usernote_note=usernote_note, usernote_warning_type=usernote_warning_type)
            db.session.add(subreddit)
            reasonEditType = 'Created'
        db.session.commit()

        notification['success'] = f'{reasonEditType} "{reason.flair_text}" for r/{reason.subreddit} successfully!'
    except Exception as error:
        notification['error'] = error
    return jsonify({'notification': notification, 'reason': reason.flair_text}), 202

@api.route('/reason/create', methods=['POST'])
@login_required
@requiresAdmin
def addReason():
    subreddit = request.form['subreddit']
    flair_text = request.form['flair_text']
    description = request.form['description']
    commentToggle = request.form['commentToggle'] == 'true'
    if commentToggle:
        commentInput = request.form['commentInput']
    else:
        commentInput = None
    lockToggle = request.form['lockToggle'] == 'true'
    commentLockToggle = request.form['commentLockToggle'] == 'true'
    banToggle = request.form['banToggle'] == 'true'
    if banToggle:
        ban_duration = request.form['ban_duration']
        ban_reason = request.form['ban_reason']
        ban_message = request.form['ban_message']
        ban_note = request.form['ban_note']
    else:
        ban_duration = None
        ban_reason = None
        ban_message = None
        ban_note = None
    usernoteToggle = request.form['usernoteToggle'] == 'true'
    if usernoteToggle:
        usernote_note = request.form['usernote_note']
        usernote_warning_type = request.form['usernote_warning_type']
    else:
        usernote_note = None
        usernote_warning_type = None
    enableOnAdd = request.form['enableOnAdd'] == 'true'
    success = None
    error = None
    reasonExists = False
    try:
        reason = RemovalReason(subreddit=subreddit, flair_text=flair_text, description=description, comment=commentInput, lock=lockToggle, lock_comment=commentLockToggle, ban=banToggle, ban_duration=ban_duration, ban_reason=ban_reason, ban_message=ban_message, ban_note=ban_note, usernote=usernoteToggle, usernote_note=usernote_note, usernote_warning_type=usernote_warning_type, enabled=enableOnAdd)
        existing = RemovalReason.query.filter_by(subreddit=subreddit, flair_text=flair_text).first()
        if existing:
            reasonExists = True
        else:
            db.session.add(reason)
            db.session.commit()
            success = f'Created removal reason for r/{reason.subreddit} successfully!'
    except Exception as err:
        error = str(err)
    reasonData = {'id': reason.id, 'subreddit': reason.subreddit, 'flair_text': reason.flair_text, 'description': reason.description, 'comment': reason.comment, 'lock': reason.lock, 'lock_comment': reason.lock_comment, 'ban': reason.ban, 'ban_duration': reason.ban_duration, 'ban_reason': reason.ban_reason, 'ban_message': reason.ban_message, 'ban_note': reason.ban_note, 'usernote': reason.usernote, 'usernote_note': reason.usernote_note, 'usernote_warning_type': reason.usernote_warning_type, 'enabled': reason.enabled}
    return jsonify({'success': success, 'error': error, 'reasonExists': reasonExists, 'reason': reasonData}), 202

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