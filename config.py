import os

CSRF_ENABLED = True
SECRET_KEY = 'lyUEbklKUptSZcwz'

MAX_CONTENT_LENGTH = 10 * 1024 * 1024

basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_PATH = os.path.join(basedir, 'app/static/images/goods')

SQLALCHEMY_DATABASE_URI = 'mysql://root:redfire0911@localhost:3306/CMall?charset=utf8'
SQLALCHEMY_TRACK_MODIFICATIONS = True
