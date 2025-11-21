from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Create uninitialized extension instances
db = SQLAlchemy()
migrate = Migrate()
