from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required

from . import auth_blueprint as auth
from .forms import RegisterForm, LoginForm, EmailForm, ResetPasswordForm
from ..models import User
from .. import db
from ..libs.email import send_mail


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if (request.method == 'POST') and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if (user is not None) and user.check_password(form.password.data):
            login_user(user, remember=True)
            next_ = request.args.get('next')
            # not next_.startswith('/') 防止重定向攻击
            if (next_ is None) or (not next_.startswith('/')):
                next_ = url_for('book.index')
            return redirect(next_)
        else:
            flash('you need register before login')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('book.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if (request.method == 'POST') and form.validate():
        with db.auto_commit():
            user = User()
            user.set_attrs(form.data)
            db.session.add(user)
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth.route('/personal_center')
def personal_center():
    pass


@auth.route('/change_password')
def change_password():
    pass


@auth.route('/reset/password', methods=['GET', 'POST'])
def forget_password_request():
    form = EmailForm(request.form)
    if request.method == 'POST':
        if form.validate():
            email = form.email.data
            user = User.query.filter_by(email=email).first_or_404()
            send_mail(email, 'reset user password', 'email/reset_password.html', user=user, token=user.gen_token())
            flash(f'We\'ll send an email to the {email}, open it up to reset your password')

    return render_template('auth/forget_password_request.html', form=form)


@auth.route('/reset/password/<token>', methods=['GET', 'POST'])
def forget_password(token):
    form = ResetPasswordForm(request.form)
    if (request.method == 'POST') and form.validate():
        if User.reset_password(token, form.password1.data):
            flash('your password has been reset successfully')
            return redirect(url_for('auth.login'))
        else:
            flash('your password has been reset failed')

    return render_template('auth/forget_password.html', form=form)

