from flask import request, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, logout_user, login_user, current_user

from . import auth_bp as auth
from .forms import LoginForm, RegisterForm, EmailForm, ResetPasswordForm, ChangePasswordForm
from ..models import User, db
from ..utils.email import send_mail


def _login(form):
    next_ = ''
    user = User.query.filter_by(email=form.email.data).first()
    if user is None:
        flash('请先完成注册，再进行登录')
        return next_

    if not user.check_password(form.password.data):
        flash('邮箱和密码不匹配，请重试')
        return next_

    if not user.confirmed:
        send_mail(user.email, '点击以激活你的帐号', 'email/confirm_account.html',
                  user=user, token=user.gen_token())
        flash(f'你的帐号尚未激活, 我们将会发送确认邮件到你的邮箱{user.email},请根据邮件提示激活帐号')
        return next_

    login_user(user, remember=True)
    next_ = request.args.get('next')
    # not next_.startswith('/') 防止重定向攻击
    if (next_ is None) or (not next_.startswith('/')):
        next_ = url_for('book.index')

    return next_


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash(f'已将处于登录状态的帐号({current_user.nickname})登出')
        logout_user()
    form = LoginForm(request.form)
    if (request.method == 'POST') and form.validate():
        next_ = _login(form)
        if next_:
            return redirect(next_)

    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if (request.method == 'POST') and form.validate():
        user = User()
        user.email = form.email.data
        user.nickname = form.nickname.data
        user.password = form.password.data
        send_mail(user.email, '点击以激活你的帐号', 'email/confirm_account.html',
                  user=user, token=user.gen_token())

        with db.auto_commit():
            db.session.add(user)
        flash(f'我们将会发送确认邮件到你的邮箱{user.email},请根据邮件提示激活帐号')

    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
def confirm(token):
    msg = '帐号激活失败'
    data = User.parse_token(token)
    if data:
        user = User.query.filter_by(email=data['email']).first()
        if user is not None:
            if user.confirmed:
                msg = '你的帐号已激活, 请勿重复操作'
            else:
                user.confirm()
                msg = '你的帐号已激活'

    flash(msg)

    return redirect(url_for('auth.login'))


@auth.route('/personal_center')
@login_required
def personal_center():
    return render_template('auth/personal.html', user=current_user.summary)


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if (request.method == 'POST') and form.validate():
        with db.auto_commit():
            current_user.password = form.new_password1.data
        flash('密码更改成，请重新登录')
        return redirect(url_for('auth.login'))

    return render_template('auth/change_password.html', user=current_user, form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('book.index'))


@auth.route('/reset/password', methods=['GET', 'POST'])
def forget_password_request():
    form = EmailForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            send_mail(user.email, '重置你的密码', 'email/reset_password.html', user=user, token=user.gen_token())
            flash(f'我们将会发送确认邮件到你的邮箱{user.email},请根据邮件提示重置密码')
        else:
            flash('请确认你的邮箱地址')

    return render_template('auth/forget_password_request.html', form=form)


@auth.route('/reset/password/<token>', methods=['GET', 'POST'])
def forget_password(token):
    form = ResetPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        data = User.parse_token(token)
        if data:
            user = User.query.get(data['id'])
            if user is not None:
                user.reset_password(form.password1.data)
                flash('帐号密码重置成功')
                return redirect(url_for('auth.login'))
            flash('帐号密码重置失败')
        else:
            flash('帐号密码重置失败')

    return render_template('auth/forget_password.html', form=form)
