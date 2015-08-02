# -*- coding:utf-8 -*-
from flask import Blueprint

# 建立main蓝图，名字为main
main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission

# 将权限的常数传给模板系统
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
