from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from app.extensions import db, migrate
from app.views import main_bp
import logging
import os
from app.db_client.db_client import DBClient


logging.basicConfig(level=logging.DEBUG)

socket = SocketIO(cors_allowed_origins="*", async_mode="eventlet")

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    app.config.from_object('config.DevConfig')
    app.logger.info("Initializing Flask app")
    db.init_app(app)
    app.sheet_registry = {}
    migrate.init_app(app, db)
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
    socket.init_app(app, message_queue=f"{redis_url}/0")
    app.db_client = DBClient(db.session)
    app.register_blueprint(main_bp)
    from app import sockets 
    app.logger.info("App created successfully.")
    return app, socket