# -*- coding:utf-8 -*-

from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm

"""
登陆相关的路由
"""

# 登录
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or 
                url_for('main.index'))
        flash(u'无效的用户名或者密码不正确')
    return render_template('auth/login.html', form=form)

# 登出
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已经登出')
    return redirect(url_for('main.index'))


# 新用户注册
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, u'请验证您的邮箱',
                   'auth/email/confirm', user=user, token=token)
        flash(u'请到注册使用的邮箱中验证您的账户')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

# 验证 用户点击邮箱中的链接验证
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash(u'您的账号已验证')
    else:
        flash(u'验证链接无效或者已过期，请重新验证')
    return redirect(url_for('main.index'))

# 验证 重新发送验证URL
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, u'请验证您的账号',
               'auth/email/confirm', user=current_user, token=token)
    flash(u'验证邮件已经发送至您注册使用的邮箱')
    return redirect(url_for('main.index'))


# 注册但是未验证的用户 只能访问 auth. 或者 static 或者 unconfirmed页面
@auth.before_app_request
def before_request():
    if current_user.is_authenticated() \
        and not current_user.confirmed \
        and request.endpoint[:5] != 'auth.' \
        and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

# 未验证用户和非匿名用户只能访问 unconfirmed页面
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
