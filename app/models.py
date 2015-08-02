# -*- coding:utf-8 -*-
from . import db, login_manager
# 导入处理密码hash的函数
from werkzeug.security import generate_password_hash, check_password_hash
# 处理用户登录
from flask.ext.login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

"""
单独的数据库模块
"""

# 用户角色表
class Role(UserMixin, db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name
    
    
# 用户信息表
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)

    # 储存密码的hash码
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User %r>' %self.username

    # 密码 不可获取
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # 密码 可以设置，输入密码，储存哈希码
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 密码 验证真伪
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 验证 生成验证码
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    # 验证 验证 验证码
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.sessionl.add(self)
        return True

# 根据用户ID得到用户对象
# 登录
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

