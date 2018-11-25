from threading import Thread

from flask_mail import Message
from flask import render_template, current_app

from .. import mail


def send_async_mail(msg, app):
    with app.app_context():
        try:
            mail.send(msg)
        except:
            pass


def send_mail(to, subject, template, **kwargs):
    msg = Message('[鱼书]' + ' ' + subject, sender=current_app.config['MAIL_USERNAME'], recipients=[to])
    msg.html = render_template(template, **kwargs)
    app = current_app._get_current_object()
    t = Thread(target=send_async_mail, args=(msg, app))
    t.start()
    t.join()


