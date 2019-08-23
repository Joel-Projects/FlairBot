from flask import Flask, session, redirect, request, url_for, render_template, Response, jsonify, Markup, flash, g
from functools import wraps
import flask


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated
