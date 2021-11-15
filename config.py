import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('CLEARDB_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'local.db')
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.split("?")[0]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
