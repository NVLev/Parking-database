import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    # SQLALCHEMY_DATABASE_URI = os.environ.get(
        # "DATABASE_URL")  # надо - отдельно TEST_DATABASE_URL

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,

    'default': TestingConfig}

    # SECRET_KEY = os.getenv('SECRET_KEY')
    # DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
