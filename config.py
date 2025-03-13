class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = "guess-me"
    SQLALCHEMY_DATABASE_URI = "sqlite:///content.db"
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 280}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    DEBUG_TB_ENABLED = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///testdb.sqlite"
    BCRYPT_LOG_ROUNDS = 1
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    DEBUG_TB_ENABLED = False
    user, password = 'mushroommotors', 'kirubinjenga'
    host = 'mushroommotors.mysql.pythonanywhere-services.com'
    db_name = 'mushroommotors$again'
    SQLALCHEMY_DATABASE_URI = f"mysql://{user}:{password}@{host}/{db_name}"