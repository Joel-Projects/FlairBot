import sentry_sdk, sys, datadog, logging.config, logging, praw, os, inspect

from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from datadog_logger import DatadogLogHandler

from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flaskext.markdown import Markdown
from flask_debugtoolbar import DebugToolbarExtension

remote = sys.platform == 'darwin'
debug = os.environ.get('FlairBotDebug', None) or True

dsn = 'https://c9c6048b785542d99466b1bc74a3f3cb@sentry.jkpayne.com/20'
config = {"version": 1, "formatters": {"default": {"format": "%(asctime)s | %(levelname)-8s | %(message)s", "datefmt": "%m/%d/%Y %I:%M:%S %p"}}, "handlers": {"consoleHandler": {"class": "logging.StreamHandler", "level": ('INFO', 'DEBUG')[sys.platform == 'darwin'], "formatter": "default", "stream": "ext://sys.stdout"}}, "loggers": {'FlairBotMgmt': {"level": "INFO", "handlers": ["consoleHandler"]}}}
sentry_logging = LoggingIntegration(level=logging.INFO)
logging.config.dictConfig(config)

log = logging.getLogger('FlairBotMgmt')
datadog.initialize(api_key="cc7f275520a6b56dc4dd1b5abefe34e5", app_key="c77a440138e4130e98963b9f075c3a8e51036a91")
log.addHandler(DatadogLogHandler(level=logging.WARNING))
if not remote:
    sentry_sdk.init(dsn=dsn, integrations=[sentry_logging, FlaskIntegration()], attach_stacktrace=True)#, before_send=before_send, before_breadcrumb=before_breadcrumb)

db = SQLAlchemy()

reddit = praw.Reddit('Lil_SpazJoekp')
from . import blueprints
from .models import User

app = Flask(__name__, static_folder='./static')
app.url_map.strict_slashes = False
app.jinja_env.cache = {}
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.auto_reload = True
app.config['SECRET_KEY'] = b"\xf05s\\\x07\xddAM\xb6\xf4x]qOf\xb3\x03\xa1\xdf:\x19K'\x99\xd8%\x17n\x84\xf7+V\xf3/H\xebi'\x94\xee\x06\x9fB\x81\x19(\xca\xd0\x10\xef\xd2\xf1Rk\xbc\x8e\xb2-/D\xc5\xe4\x92\x91"

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://flairbot:52939L%t6eV3910t@digitalocean.jkpayne.com/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = app.config['DEBUG_TB_PROFILER_ENABLED'] = debug
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.debug = remote
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

db.init_app(app)
Markdown(app)
if debug:
    DebugToolbarExtension().init_app(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

isBlueprint = lambda blueprint: (isinstance(blueprint, Blueprint))
blueprints = [blueprint[1] for blueprint in inspect.getmembers(blueprints, isBlueprint)]
for blueprint in blueprints:
    app.register_blueprint(blueprint)