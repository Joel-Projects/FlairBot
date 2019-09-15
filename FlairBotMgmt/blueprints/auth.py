from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from . import *

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter(User.username.ilike(request.form['username'])).first()

        if user and check_password_hash(user.password, password) and user.enabled:
            login_user(user, remember=remember, fresh=False)
            return redirect(url_for('main.dash'))
        elif not user.enabled:
            flash('Your account is disabled.')
            return render_template('login.html', username=username, password=password)
        else:
            flash('Please check your login details and try again.')
            return render_template('login.html', username=username, password=password)

    return render_template('login.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

