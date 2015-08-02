# -*- coding:utf-8 -*-
from . import db, login_manager
# 导入处理密码hash的函数
from werkzeug.security import generate_password_hash, check_password_hash
# 处理用户登录
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# current_app 从flask 中，而current_user 从login中
from flask import current_app, request
from datetime import datetime
import hashlib

"""
单独的数据库模块
"""

# 定义权限对应的数
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

# 用户角色表
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    # 记录是否时默认的权限，在初始化用户时设定
    default = db.Column(db.Boolean, default=False, index=True)
    # 记录权限数字
    permissions = db.Column(db.Integer)

    def __repr__(self):
        return '<Role %r>' % self.name

    # 插入角色，静态方法
    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT | 
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if  role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()
    
    
# 用户信息表
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    # 详细个人信息
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    # 初始化用户，设定默认权限
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.role:
            if self.email == current_app.config['XBLOG_ADMIN']:
                self.role = Role.query.filter_by(permission=0xff).first()
            if not self.role:
                self.role = Role.query.filter_by(default=True).first()


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
        db.session.add(self)
        return True

    # 用户的权限
    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    # 刷新登录时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    # 个人头像
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


# 匿名用户类的权限
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
# 匿名用户的loader
login_manager.anonymous_user = AnonymousUser

# 根据用户ID得到用户对象
# 登录
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


