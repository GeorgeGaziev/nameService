from flask import Flask
from config import Config
from flask_assets import Environment, Bundle

app = Flask(__name__)
app.config.from_object(Config)
assets = Environment(app)


js = Bundle('bundle.js', output='static/bundle.js')
assets.register('js_all', js)

from app import routes