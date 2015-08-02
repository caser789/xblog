# -*- coding:utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


# 登录的表单
# 四个组件：邮件，密码，是否记住，提交按钮
class LoginForm(Form):
    email = StringField(u'电子邮箱地址', validators=[Required(), Length(1, 64),
                        Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'保持登录')
    submit = SubmitField(u'登录')

# 用户注册的表单
class RegistrationForm(Form):
    email = StringField(u'电子邮箱地址', validators=[Required(), Length(1, 64), 
                                            Email()])
    username = StringField(u'用户名', validators=[Required(),
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
        u'用户名中只能含有字母，数字和下划线')])
    password = PasswordField(u'密码', validators=[Required(),
        EqualTo('password2', message=u'两次输入的密码不一致.')])
    password2 = PasswordField(u'验证密码', validators=[Required()])
    submit = SubmitField(u'注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱地址已注册。')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已注册')
            
