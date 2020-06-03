CSRF_ENABLED = True
SECRET_KEY = 'lyUEbklKUptSZcwz'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'mysql://root:redfire0911@localhost:3306/CMall?charset=utf8'
SQLALCHEMY_TRACK_MODIFICATIONS = True