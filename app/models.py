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
from markdown import markdown
import bleach
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

# secondary table of self ref ralationship of user
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
        primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
        primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

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
    # 储存头像 的哈希码，减少载入页面时的计算
    avatar_hash = db.Column(db.String(32))
    # 加入帖子 属性
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # self ref relationship
    followd = db.relationship('Follow', foreign_keys=[Follow.follower_id],
        backref=db.backref('follower', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
        backref=db.backref('followed', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')
    
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follwer=self,follower=user)
            db.session.add(f)
    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is \
            not None
    # define as a property to keep consistency
    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == 
            Post.author_id).filter(Follow.follower_id == self.id)


    # 初始化用户，设定默认权限
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
    #初始化角色
        if not self.role:
            if self.email == current_app.config['XBLOG_ADMIN']:
                self.role = Role.query.filter_by(permission=0xff).first()
            if not self.role:
                self.role = Role.query.filter_by(default=True).first()
        if self.email and not self.avatar_hash:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        self.followed.append(Follow(followed=self))


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
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)
    # 生成测试用的 假数据
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    @staticmethod
    def add_self_follow():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit() 



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

# 帖子的model
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # 储存 markdown
    body_html = db.Column(db.Text)

    def __repr__(self):
        return '<Post %r>' %self.body

    # 生成 测试用的假数据
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
            'em', 'i', 'li', 'ol','pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, 
        output_format='html'), tags=allowed_tags, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)


