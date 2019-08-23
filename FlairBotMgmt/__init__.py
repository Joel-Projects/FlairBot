from flask import Flask
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey111'
import FlairBotMgmt.main
import FlairBotMgmt.sessionhandler
import FlairBotMgmt.decorators_special
