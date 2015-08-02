# -*- coding:utf-8 -*-
from threading import Thread
from flask import current_app, render_template
from flask.ext.mail import Message
from . import mail

"""
单独的邮件处理模块
可以多线程发送邮件
由于邮件需要在激活的app环境下发送
需要调用current_app来在每个线程中建立context
"""

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    # 重要！ 获取当前app
    app = current_app._get_current_object()
    msg = Message(app.config['XBLOG_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['XBLOG_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
    
