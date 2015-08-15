# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Permission, Post, Follow, Comment
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

# 用config或者环境变量建立app
app = create_app(os.getenv('XBLOG_CONFIG') or 'default')
# 添加命令行功能
manager = Manager(app)
# 添加数据库版本管理
migrate = Migrate(app, db)

# 添加数据库版本管理功能到命令行
# 在命令行中自动导入调试需要的内容，比如数据库中的用户，数据库
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, 
        Permission=Permission, Post=Post, Follow=Follow, Comment=Comment)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

# 添加单元测试命令到命令行，注意与添加shell db 命令的区别
@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

# auto deploy
@manager.command
def deploy():
    """Run deployment task"""
    from flask.ext.migrate import upgrade
    from app.models import Role, User
    upgrade()
    Role.insert_roles()
    User.add_self_follow()

if __name__ == '__main__':
    manager.run()
