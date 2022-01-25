import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_PATH')
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.split("?")[0]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 100, 'pool_recycle': 1800}
