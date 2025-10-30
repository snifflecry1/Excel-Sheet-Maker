from flask import Flask
from flask_socketio import SocketIO
from app.extensions import db, migrate
from app.views import main_bp
import logging
import os

redis_url = os.getenv("REDIS_URL", "redis://redis:6379")

logging.basicConfig(level=logging.DEBUG)
socket = SocketIO(cors_allowed_origins="*")

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.DevConfig')

    app.logger.info(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    db.init_app(app)
    migrate.init_app(app, db)
    socket.init_app(app, message_queue="redis://redis:6379/0")

    app.register_blueprint(main_bp)
    from app import sockets 
    return app, socket