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
        flash('无效的用户名或者密码不正确')
    return render_template('auth/login.html', form=form)

# 登出
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已经登出')
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
        flash('感谢您的注册，请登录！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
