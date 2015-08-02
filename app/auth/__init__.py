# -*- coding:utf-8 -*-
from flask import Blueprint

"""
初始化专门处理登陆的auth蓝图
"""

auth = Blueprint('auth', __name__)

from . import views
