import praw
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from flask_login import login_required, current_user
from . import *

subreddits = Blueprint('subreddits', __name__, url_prefix='/subreddits')

@subreddits.route('/')
@login_required
def root():
    subreddits = Subreddit.query.order_by(Subreddit.id).all()
    removalReasons = RemovalReason.query.order_by(RemovalReason.id).all()

    reasonCounts = {}
    for reason in removalReasons:
        if not reason.subreddit in reasonCounts:
            reasonCounts[reason.subreddit] = 0
        reasonCounts[reason.subreddit] += 1
    return render_template('subreddits.html', subreddits=subreddits, reasonCounts=reasonCounts)


def validateRedditor(redditor):
    try:
        response = requests.get(f"https://reddit.com/user/{redditor}/about.json", headers={'user-agent': 'python:com.jkpayne.redditapps/FlairBot by /u/Lil_SpazJoekp'})
        while response.status_code not in (200, 403, 404):
            response = requests.get(f"https://reddit.com/user/{redditor}/about.json", headers={'user-agent': 'python:com.jkpayne.redditapps/FlairBot by /u/Lil_SpazJoekp'})
        redditor = response.json()['data']['name']
    except KeyError:
        return None
    return redditor

@subreddits.route('/<subreddit>', methods=['GET', 'POST'])
@login_required
@validateSubreddit
def viewSubreddit(subreddit):
    session['subreddit'] = subreddit
    notification = {'success': None, 'error': None}
    subreddit = Subreddit.query.filter_by(subreddit=subreddit).first()
    removalReasons = RemovalReason.query.filter_by(subreddit=subreddit.subreddit).all()
    if subreddit:
        if request.method == 'POST':
            bot_account = validateRedditor(request.form['botAccount'])
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
                    subredditEditType = 'Created'
                db.session.commit()

                notification['success'] = f'{subredditEditType} r/{subreddit.subreddit} successfully!'
            except Exception as error:
                notification['error'] = error
        return render_template('edit_subreddit.html', subreddit=subreddit, notification=notification, removalReasons=removalReasons), 202
    return render_template('errors/404.html'), 404