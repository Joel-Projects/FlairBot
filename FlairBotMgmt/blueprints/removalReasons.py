import praw
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .. import reddit
from . import *

removalReasons = Blueprint('removalReason', __name__, url_prefix='/reasons')

@removalReasons.route('/')
@login_required
def root():
    removalReasons = RemovalReason.query.all()
    subreddits = Subreddit.query.all()
    return render_template('removal_reasons.html', removalReasons=removalReasons, subreddits=subreddits)

@removalReasons.route('/<reason_id>', methods=['GET', 'POST'])
@login_required
def viewRemovalReason(reason_id):
    session['reason_id'] = reason_id
    notification = {'success': None, 'error': None}
    removalReason = RemovalReason.query.filter_by(id=reason_id).first()
    reasonSubreddit = Subreddit.query.filter_by(subreddit=removalReason.subreddit).first()
    subreddits = Subreddit.query.all()
    if removalReason:
        if request.method == 'POST':
            reasonId = reason_id
            subreddit = request.form['subreddit']
            flair_text = request.form['flair_text']
            description = request.form['description']
            commentToggle = request.form.get('commentToggle') == 'on'
            if commentToggle:
                commentInput = request.form['commentText']
            else:
                commentInput = None
            lockToggle = request.form.get('lockToggle') == 'true'
            commentLockToggle = request.form.get('commentLockToggle') == 'on'
            banToggle = request.form.get('banToggle') == 'true'
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
            usernoteToggle = request.form.get('usernoteToggle') == 'on'
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
        return render_template('edit_removal_reason.html', removalReason=removalReason, notification=notification, subreddits=subreddits, subreddit=reasonSubreddit), 202
    return render_template('errors/404.html'), 404

@removalReasons.route('/new', methods=['GET', 'POST'])
@login_required
def newRemovalReason():
    removalReason = None
    notification = None
    subreddits = Subreddit.query.all()
    return render_template('edit_removal_reason.html', removalReason=removalReason, notification=notification, subreddits=subreddits), 202