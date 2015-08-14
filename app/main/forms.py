# -*- coding:utf-8 -*-
from flask.ext.wtf import Form
from flask.ext.pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, \
    SelectField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User

"""
单独的处理表单的模块
"""

# 一个简单的提交姓名的表单 :)
class NameForm(Form):
    name = StringField(u'姓名', validators=[Required()])
    submit = SubmitField(u'提交')

# 编辑个人信息的表
class EditProfileForm(Form):
    name = StringField(u'真实姓名', validators=[Length(0, 64)])
    location = StringField(u'住址', validators=[Length(0, 64)])
    about_me = TextAreaField(u'个人简介')
    submit = SubmitField(u'提交')

# 编辑个人信息表  管理员
class EditProfileAdminForm(Form):
    email = StringField(u'邮箱地址', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField(u'昵称', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
        u'用户名只能由字母，数字和下划线组成')])
    confirmed = BooleanField(u'是否验证')
    # 一个下拉选择菜单
    role = SelectField(u'角色', coerce=int)
    name = StringField(u'真实姓名', validators=[Length(0, 64)])
    location = StringField(u'地址', validators=[Length(0, 64)])
    about_me = TextAreaField(u'个人简介')
    submit = SubmitField(u'提交')

    # 这个表要传入 user
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        # 提供选择的内容，包括id 和 name
        self.role.choices = [(role.id, role.name) for role in 
            Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
            User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱地址已注册')
    def validate_username(self, field):
        if filed.data != self.user.username and \
            User.query.filter_by(username=field.data).first():
            raise ValidationError(u'昵称已存在')

# 帖子提交 表
class PostForm(Form):
    body = PageDownField(u'说点什么吧:)', validators=[Required()])
    submit = SubmitField(u'提交')

class CommentForm(Form):
    body = StringField(u'开始评头论足吧...', validators=[Required()])
    submit=SubmitField(u'提交评论')
