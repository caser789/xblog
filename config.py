# -*- coding:utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "xuejiao's blog"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT =  25 #465  994 or 25
    MAIL_USE_TLS = False 
    MAIL_USERNAME =  os.environ.get('_163_USERNAME') 
    MAIL_PASSWORD =  os.environ.get('_163_PASSWORD')
    XBLOG_MAIL_SUBJECT_PREFIX = '[XBLOG]'
    XBLOG_MAIL_SENDER = 'm13488699851@163.com'
    XBLOG_ADMIN = os.environ.get('XBLOG_ADMIN')
    XBLOG_POSTS_PER_PAGE = 20
    XBLOG_FOLLOWERS_PER_PAGE = 50 
    XBLOG_COMMENTS_PER_PAGE = 30
    

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
