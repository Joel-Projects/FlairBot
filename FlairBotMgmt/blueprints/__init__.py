import importlib, os
from .. import db
from ..decorators import *
from ..models import User, Subreddit, RemovalReason

db = db
requiresAdmin, validateSubreddit, validateSubredditForm = requiresAdmin, validateSubreddit, validateSubredditForm
User, Subreddit, RemovalReason = User, Subreddit, RemovalReason

blueprints = [i[:-3] for i in os.listdir(os.path.join(os.path.curdir, 'FlairBotMgmt', 'blueprints')) if i != '__init__.py' and i != '__pycache__']
for blueprint in blueprints:
    importlib.import_module(f'.{blueprint}', 'FlairBotMgmt.blueprints')

