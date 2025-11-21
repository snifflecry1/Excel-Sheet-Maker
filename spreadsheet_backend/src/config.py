import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "postgresql://test:test@db:5432/test"
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False
