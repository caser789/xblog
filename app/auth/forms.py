# -*- coding:utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email

# 登录的表单
# 四个组件：邮件，密码，是否记住，提交按钮
class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                        Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

