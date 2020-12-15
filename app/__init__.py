from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

app = Flask(__name__)
app.config.from_object(Config)
app.url_map.strict_slashes = False
db = SQLAlchemy(app)
cache = Cache(app)

from app.main import routes
from app.data import models