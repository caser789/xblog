# -*- coding:utf-8 -*-
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import config

"""创建app工厂函数
初始化bootstrap, 可以在页面中调用bootstrap的base页面
初始化mail，可以给管理员发送邮件通知异常，用户注册，
也可发邮件给用户验证或者通知。
初始化Moment，在页面显示时间。
初始化数据库，使用ORM SQLAlchemy
导入配置，创建app时需要传入配置"""

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
# config_name: 配置名，对应与config中的配置dict中的key
def create_app(config_name):
    app  = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    # 注册蓝图 main
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # 注册 蓝图 auth
    # 设置 蓝图 对应的 URL 前缀
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
