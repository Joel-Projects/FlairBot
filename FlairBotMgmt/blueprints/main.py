import praw
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from flask_login import login_required, current_user
from ..models import Subreddit, RemovalReason, User

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def root():
    return render_template('dash.html')

# @main.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         permanent = request.form.get('rememberMe', None)
#         user = User.query.fil
#         if user.exists and user.checkPassword(password):
#             if user.enabled:
#                 session['username'] = user.username
#                 session['isAdmin'] = user.admin
#                 session.permanent = bool(permanent)
#                 return redirect(url_for('home'))
#             else:
#                 return jsonify({'error': 'Your account is disabled'}), 403
#         else:
#             return jsonify({'error': 'Username or password are incorrect'}), 401
#     return render_template('login.html', error=error)

@main.route('/dash')
@login_required
def dash():
    return render_template('dash.html')

@main.route('/reasons')
@login_required
def removalReasons():
    with conn.cursor() as sql:
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


