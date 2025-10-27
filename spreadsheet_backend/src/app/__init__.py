from flask import Flask
from app.extensions import db, migrate
from app.views import main_bp
import logging

logging.basicConfig(level=logging.DEBUG)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.DevConfig')

    app.logger.info(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main_bp)

    
    return app