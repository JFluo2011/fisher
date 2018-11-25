DEBUG = False
SECRET_KEY = 'hard to guess string'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/fisher'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_COMMIT_ON_TEARDOWN = True

try:
    from .local_security import *
except:
    pass
