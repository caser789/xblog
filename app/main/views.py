# -*- coding:utf-8 -*-

from flask import render_template
from . import main

"""
main中的路由
处理请求，返回对应的表单和页面
"""

# 主页
@main.route('/')
def index():
    return render_template('index.html')
