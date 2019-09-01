from . import db
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Flairlog(Base):
    __tablename__ = 'flairlog'
    __table_args__ = {'schema': 'flairbots'}
    id = db.Column(db.CHAR(36), primary_key=True)
    created_utc = db.Column(TIMESTAMP(True, 4))
    moderator = db.Column(db.String(22), nullable=False)
    subreddit = db.Column(db.String(22), nullable=False)
    target_author = db.Column(db.String(22))
    target_body = db.Column(db.Text)
    target_id = db.Column(db.Text)
    target_permalink = db.Column(db.Text)
    target_title = db.Column(db.Text)
    flair = db.Column(db.Text)

class Subreddit(db.Model):
    __tablename__ = 'subreddits'
    __table_args__ = {'schema': 'flairbots'}
    id = db.Column(db.Integer, nullable=False, server_default=db.text("nextval('flairbots.subreddits_id_seq'::regclass)"))
    subreddit = db.Column(db.String(24), primary_key=True)
    bot_account = db.Column(db.String(24), nullable=False)
    webhook = db.Column(db.Text)
    webhook_type = db.Column(db.Text)
    header = db.Column(db.Text)
    footer = db.Column(db.Text)
    enabled = db.Column(db.Boolean, server_default=db.text("false"))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'flairbots'}
    id = db.Column(db.Integer, nullable=False, primary_key=True, server_default=db.text("nextval('flairbots.users_id_seq'::regclass)"))
    username = db.Column(db.Text)
    password = db.Column(db.Text, nullable=False)
    admin = db.Column(db.Boolean, server_default=db.text("false"))
    created = db.Column(db.DateTime(True), server_default=db.text("now()"))
    updated = db.Column(db.DateTime(True))
    updatedby = db.Column(db.Text)
    enabled = db.Column(db.Boolean, server_default=db.text("true"))

class RemovalReason(db.Model):
    __tablename__ = 'removal_reasons'
    __table_args__ = {'schema': 'flairbots'}
    id = db.Column(db.Integer, primary_key=True, server_default=db.text("nextval('flairbots.removal_reasons_id_seq'::regclass)"))
    subreddit = db.Column(db.ForeignKey('flairbots.subreddits.subreddit', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    flair_text = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, comment='This is the description sent to the log channel')
    comment = db.Column(db.Text)
    lock = db.Column(db.Boolean)
    lock_comment = db.Column(db.Boolean)
    ban = db.Column(db.Boolean)
    ban_duration = db.Column(db.Integer, comment='Ban duration in days, 0 for permanent.')
    ban_reason = db.Column(db.Text, comment='Subreddit/site rule broken or other.')
    ban_message = db.Column(db.Text, comment='Message that is sent to the user')
    ban_note = db.Column(db.Text, comment='Mod note. Not visible to user.')
    usernote = db.Column(db.Boolean)
    usernote_note = db.Column(db.Text)
    usernote_warning_type = db.Column(db.Text, comment='Type of note. Must exactly match toolbox note types. Null for no type.')
    # subreddit1 = db.relationship('subreddits')