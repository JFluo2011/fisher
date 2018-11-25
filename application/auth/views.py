from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required

from . import auth_blueprint as auth
from .forms import RegisterForm, LoginForm
from ..models import User
from .. import db


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


@auth.route('/forget_password_request')
def forget_password_request():
    pass

