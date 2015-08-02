# -*- coding:utf-8 -*-
from . import db
# 导入处理密码hash的函数
from werkzeug.security import generate_password_hash, check_password_hash

"""
单独的数据库模块
"""

# 用户角色表
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    # 储存密码的hash码
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<Role %r>' % self.name
    
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

# 用户信息表
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' %self.username
