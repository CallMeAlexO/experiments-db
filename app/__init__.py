import os

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
import logging

db = SQLAlchemy()
log = logging
dirname = os.path.dirname(os.path.abspath(__file__))


def create_app(config_class=Config):
    app = Flask(__name__, static_folder=os.path.join(dirname, "static"))
    app.config.from_object(config_class)

    db.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
