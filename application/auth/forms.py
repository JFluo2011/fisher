from wtforms import StringField, PasswordField, Form
from wtforms.validators import Length, DataRequired, Email, EqualTo
from wtforms.validators import ValidationError

from ..models import User


class EmailForm(Form):
    email = StringField(validators=[Length(min=8, max=64), DataRequired(), Email(message='invalid email address')])


class RegisterForm(Form):
    email = StringField(validators=[Length(min=8, max=64), DataRequired(), Email(message='invalid email address')])
    password = PasswordField(validators=[
        Length(6, 32),
        DataRequired(message='password can\'t be blank and must contain 6-32 characters')
    ])
    nickname = StringField(validators=[Length(2, 10, message='nickname must contain 2-8 characters'), DataRequired()])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('email has already been registered')

    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError('nickname has already been taken')


class LoginForm(EmailForm):
    password = PasswordField(validators=[
        Length(6, 32),
        DataRequired(message='password can\'t be blank and must contain 6-32 characters')
    ])


class ResetPasswordForm(Form):
    password1 = PasswordField(validators=[
        Length(6, 32),
        DataRequired(message='password can\'t be blank and must contain 6-32 characters'),
        EqualTo('password2', message='password does not match the confirm password')
    ])
    password2 = PasswordField(validators=[
        Length(6, 32),
        DataRequired()
    ])

