from flask import Blueprint, jsonify, request,
from flask_login import login_required
from . import *

reason = Blueprint('reason_api', __name__, url_prefix='/api/reason')

@reason.route('/create', methods=['POST'])
@login_required
@requiresAdmin
def createReason():
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
        reason = RemovalReason(subreddit=subreddit, flair_text=flair_text.lower(), description=description, comment=commentInput, lock=lockToggle, lock_comment=commentLockToggle, ban=banToggle, ban_duration=ban_duration, ban_reason=ban_reason, ban_message=ban_message, ban_note=ban_note, usernote=usernoteToggle, usernote_note=usernote_note, usernote_warning_type=usernote_warning_type, enabled=enableOnAdd)
        existing = RemovalReason.query.filter_by(subreddit=subreddit, flair_text=flair_text).first()
        if existing:
            reasonExists = True
        else:
            db.session.add(reason)
            db.session.commit()
            success = f'Created removal reason for r/{reason.subreddit} successfully!'
    except Exception as err:
        error = str(err)
    reasonData = {'id': reason.id, 'subreddit': reason.subreddit, 'flair_text': reason.flair_text, 'description': reason.description, 'comment': reason.comment, 'lock': reason.lock, 'lock_comment': reason.lock_comment, 'ban': reason.ban, 'ban_duration': reason.ban_duration, 'ban_reason': reason.ban_reason, 'ban_message': reason.ban_message, 'ban_note': reason.ban_note, 'usernote': reason.usernote, 'usernote_note': reason.usernote_note, 'usernote_warning_type': reason.usernote_warning_type,
                  'enabled': reason.enabled}
    return jsonify({'success': success, 'error': error, 'reasonExists': reasonExists, 'reason': reasonData}), 202

@reason.route('/edit', methods=['POST'])
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
            reason.flair_text = flair_text.lower()
            reason.description = description
            reason.comment = commentInput
            reason.lock = lockToggle
            reason.lock_comment = commentLockToggle
            reason.ban = banToggle
            reason.ban_duration = ban_duration
            reason.ban_reason = ban_reason
            reason.ban_message = ban_message
            reason.ban_note = ban_note
            reason.usernote = usernoteToggle
            reason.usernote_note = usernote_note
            reason.usernote_warning_type = usernote_warning_type
            db.session.merge(reason)
            reasonEditType = 'Updated'
        else:
            reason = RemovalReason(subreddit=subreddit, flair_text=flair_text.lower(), description=description, comment=commentInput, lock=lockToggle, lock_comment=commentLockToggle, ban=banToggle, ban_duration=ban_duration, ban_reason=ban_reason, ban_message=ban_message, ban_note=ban_note, usernote=usernoteToggle, usernote_note=usernote_note, usernote_warning_type=usernote_warning_type)
            db.session.add(subreddit)
            reasonEditType = 'Created'
        db.session.commit()

        notification['success'] = f'{reasonEditType} "{reason.flair_text}" for r/{reason.subreddit} successfully!'
    except Exception as error:
        notification['error'] = error
    return jsonify({'notification': notification, 'reason': reason.flair_text}), 202

@reason.route('/delete', methods=['POST'])
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

@reason.route('/toggle', methods=['POST'])
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