import praw
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from flask_login import login_required, current_user
from ..models import Subreddit, RemovalReason, User

removalReason = Blueprint('removalReason', __name__, url_prefix='/reasons')

@removalReason.route('/')
@login_required
def root():
    subreddits = Subreddit.query.all()
    removalReasons = RemovalReason.query.all()

    reasonCounts = {}
    for reason in removalReasons:
        if not reason.subreddit in reasonCounts:
            reasonCounts[reason.subreddit] = 0
        reasonCounts[reason.subreddit] += 1
    return render_template('subreddits.html', subreddits=subreddits, reasonCounts=reasonCounts)