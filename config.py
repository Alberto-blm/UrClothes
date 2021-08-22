import os

DB_USER = "admin"
DB_PASSWORD = "altair98"
SECRET_KEY = "Ropita"

class Config(object):
    DEBUG = False
    SECRET_KEY = 'dev'

    #PLATZI_DB_URI = os.environ['PLATZI_DB_URI']


class DevelopmentConfig(Config):
    DEBUG = False

