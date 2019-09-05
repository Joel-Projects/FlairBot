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
    subreddits = Subreddit.query.all()
    if removalReason:
        subreddit = Subreddit.query.filter_by(subreddit=removalReason.subreddit).first()
        header = subreddit.header
        footer = subreddit.footer
        if request.method == 'POST':
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
            notification = {'success': None, 'error': None}
            try:
                if removalReason:
                    removalReason.bot_account = bot_account
                    removalReason.webhook_type = webhook_type
                    removalReason.webhook = webhook
                    removalReason.header = header
                    removalReason.footer = footer
                    db.session.merge(removalReason)
                    removalReasonEditType = 'Updated'
                else:
                    removalReason = removalReason(bot_account=bot_account, webhook_type=webhook_type, webhook=webhook, header=header, footer=footer)
                    db.session.add(removalReason)
                    removalReasonEditType = 'Created'
                db.session.commit()

                notification['success'] = f'{removalReasonEditType} r/{removalReason.removalReason} successfully!'
            except Exception as error:
                notification['error'] = error
        return render_template('edit_removal_reason.html', removalReason=removalReason, notification=notification, subreddits=subreddits), 202
    return render_template('errors/404.html'), 404

@removalReasons.route('/new', methods=['GET', 'POST'])
@login_required
def newRemovalReason():
    removalReason = None
    notification = None
    subreddits = Subreddit.query.all()
    return render_template('edit_removal_reason.html', removalReason=removalReason, notification=notification, subreddits=subreddits), 202