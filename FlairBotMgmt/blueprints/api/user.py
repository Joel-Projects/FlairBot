import praw, prawcore
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .. import *
from . import *

user = Blueprint('user_api', __name__, url_prefix='/api/user')

@user.route('/create', methods=['POST'])
@login_required
@requiresAdmin
@validateUsername
def createUser(username=None, reason=None):
    if reason:
        userData = {}
        userExists = False
        error = reason
        success = False
    elif username:
        password = request.form.get('password')
        admin = True if request.form.get('adminToggle') else False

        success = None
        error = None
        userExists = False
        try:
            user = User.query.filter_by(username=username).first()

            if user:
                userExists = True
                userData = {}
            else:
                user = User(username=username, admin=admin, password=generate_password_hash(password, "pbkdf2:sha256:80000", 80000), updatedby=current_user.username)
                db.session.add(user)
                db.session.commit()
                success = f"Created user: '{user.username}' successfully!"
                userData = {'id': user.id, 'username': user.username, 'admin': user.admin, 'created': user.created.strftime('%m/%d/%Y %I:%M:%S %p'), 'updated': user.updated.strftime('%m/%d/%Y %I:%M:%S %p'), 'updatedby': user.updatedby, 'enabled': user.enabled}
        except Exception as error:
            error = error
    return jsonify({'success': success, 'error': error, 'userExists': userExists, 'user': userData}), 202

@user.route('/edit', methods=['POST'])
@login_required
@validateUserForm
def editUser(user=None):
    username = user
    password = request.form.get('password', None)
    admin = request.form.get('adminToggle') == 'true'
    updatedby = current_user.username
    user = User.query.filter_by(username=username).first()
    success =  None
    error =  None
    userExists = False
    try:
        if user:
            user.username = username
            if password:
                password = generate_password_hash(password, "pbkdf2:sha256:80000", 80000)
            else:
                password = user.password
            user.passowrd = password
            if user.username in ('admin', 'spaz'):
                admin = True
            if current_user.admin:
                user.admin = admin
            else:
                user.admin = user.admin
            user.updatedby = updatedby
            db.session.merge(user)
            db.session.commit()
            success = f'Updated {user.username} successfully!'
            userData = {'id': user.id, 'username': user.username, 'admin': user.admin, 'created': user.created.strftime('%m/%d/%Y %I:%M:%S %p'), 'updated': user.updated.strftime('%m/%d/%Y %I:%M:%S %p'), 'updatedby': user.updatedby, 'enabled': user.enabled}
        else:
            error =  "That user doesn't exist!"
    except Exception as e:
        error = e
    return jsonify({'success': success, 'error': error, 'userExists': userExists, 'user': userData}), 202

@user.route('/delete', methods=['POST'])
@login_required
@requiresAdmin
def deleteUser():
    notification = {'success': None, 'error': None}
    username = request.form['username']
    try:
        user = User.query.filter_by(username=username).first()
        if user:
            if user.username in ('admin', 'spaz'):
                notification['error'] = 'You can\'t delete that user'
            else:
                db.session.delete(user)
                db.session.commit()
                notification['success'] = True
        else:
            notification['error'] = "That user doesn't exist"
    except Exception as error:
        notification['error'] = error
    return jsonify({'success': notification['success'], 'error': notification['error'], 'notification': notification, 'user': username}), 202

@user.route('/toggle', methods=['POST'])
@login_required
@requiresAdmin
def toggleUser():
    username = request.form['username']
    notification = {'success': None, 'error': None}
    try:
        user = User.query.filter_by(username=username).first()
        user.enabled = not user.enabled
        if user.username == 'admin' or user.username == 'spaz':
            user.enabled = True
        db.session.merge(user)
        db.session.commit()
        notification['success'] = True
    except Exception as error:
        notification['error'] = error
    return jsonify({'success': notification['success'], 'error': notification['error'], 'username': username, 'enabled': user.enabled}), 202
