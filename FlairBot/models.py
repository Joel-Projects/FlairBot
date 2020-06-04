from sqlalchemy import Boolean, CHAR, Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()
metadata = Base.metadata

class Flairlog(Base):
    __tablename__ = 'flairlog'

    __table_args__ = {'schema': 'flairbots'}

    id = Column(CHAR(36), primary_key=True)
    created_utc = Column(TIMESTAMP(True, 4))
    moderator = Column(String(22), nullable=False)
    subreddit = Column(String(22), nullable=False)
    target_author = Column(String(22))
    target_body = Column(Text)
    target_id = Column(Text)
    target_permalink = Column(Text)
    target_title = Column(Text)
    flair = Column(Text)

class Subreddit(Base):
    __tablename__ = 'subreddits'
    __table_args__ = {'schema': 'flairbots'}

    subreddit = Column(String(24), primary_key=True)
    bot_account = Column(String(24), nullable=False)
    webhook = Column(Text)
    webhook_type = Column(Text)
    header = Column(Text)
    footer = Column(Text)
    enabled = Column(Boolean, server_default=text("false"))
    id = Column(Integer, nullable=False, server_default=text("nextval('flairbots.subreddits_id_seq'::regclass)"))

class RemovalReason(Base):
    __tablename__ = 'removal_reasons'
    __table_args__ = {'schema': 'flairbots'}

    id = Column(Integer, nullable=False, server_default=text("nextval('flairbots.removal_reasons_id_seq'::regclass)"))
    subreddit = Column(ForeignKey('flairbots.subreddits.subreddit', ondelete='RESTRICT', onupdate='CASCADE'), primary_key=True, nullable=False)
    flair_text = Column(Text, primary_key=True, nullable=False)
    description = Column(Text, comment='This is the description sent to the log channel')
    comment = Column(Text)
    lock = Column(Boolean)
    lock_comment = Column(Boolean)
    ban = Column(Boolean)
    ban_duration = Column(Integer, comment='Ban duration in days, 0 for permanent.')
    ban_reason = Column(Text, comment='Subreddit/site rule broken or other.')
    ban_message = Column(Text, comment='Message that is sent to the user')
    ban_note = Column(Text, comment='Mod note. Not visible to user.')
    usernote = Column(Boolean)
    usernote_note = Column(Text)
    usernote_warning_type = Column(Text, comment='Type of note. Must exactly match toolbox note types. Null for no type.')
    enabled = Column(Boolean, server_default=text("true"))

    subreddit1 = relationship('Subreddit')
