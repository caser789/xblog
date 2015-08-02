# -*- coding:utf-8 -*-
from functools import wraps
from flask import abort
from flask.ext.login import current_user
from .models import Permission

# 传入的参数时 model 中 Permission中的常数
def permission_required(permission):
    def decorator(f):
        @wrap(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
    
