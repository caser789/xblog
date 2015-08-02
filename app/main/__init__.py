# -*- coding:utf-8 -*-
from flask import Blueprint

# 建立main蓝图，名字为main
main = Blueprint('main', __name__)

from . import views, errors
