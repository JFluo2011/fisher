# from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, Form
from wtforms.validators import Length, DataRequired, Email, ValidationError, EqualTo
from flask_login import current_user

from ..models import User


class EmailForm(Form):
    email = StringField(validators=[Email(message='错误的邮箱地址'), Length(min=8, max=64), DataRequired()])


class RegisterForm(EmailForm):
    nickname = StringField(validators=[Length(2, 20, message='昵称需要2-20个字符'), DataRequired()])
    password = PasswordField(validators=[Length(6, 32), DataRequired(message='密码不能为空，并且包含6-32个字符')])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError('昵称被占用')


class LoginForm(EmailForm):
    password = PasswordField(validators=[Length(6, 32), DataRequired(message='密码不能为空，并且包含6-32个字符')])


class ResetPasswordForm(Form):
    password1 = PasswordField(validators=[
        Length(6, 32),
        DataRequired(message='密码不能为空，并且包含6-32个字符'),
        EqualTo('password2', message='两次输入的密码不匹配')
    ])
    password2 = PasswordField(validators=[
        Length(6, 32),
        DataRequired()
    ])


class ChangePasswordForm(Form):
    old_password = PasswordField(validators=[
        Length(6, 32),
        DataRequired(message='密码不能为空，并且包含6-32个字符'),
    ])
    new_password1 = PasswordField(validators=[
        Length(6, 32),
        DataRequired(message='密码不能为空，并且包含6-32个字符'),
        EqualTo('new_password2', message='两次输入的密码不匹配')
    ])
    new_password2 = PasswordField(validators=[
        Length(6, 32),
        DataRequired()
    ])

    def validate_old_password(self, field):
        if not current_user.check_password(field.data):
            raise ValidationError('你输入的原始密码不正确')
