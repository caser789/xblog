# -*- coding:utf-8 -*-

from flask import render_template
from . import auth

"""
登陆相关的路由
"""

@auth.route('/login')
def login():
    return render_template('auth/login.html')
