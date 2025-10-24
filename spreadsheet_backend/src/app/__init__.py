from flask import Flask
from .extensions import db, migrate
from .routes import urls

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.DevConfig')

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(urls)

    
    return app