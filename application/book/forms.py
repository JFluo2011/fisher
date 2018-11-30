# from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, Form
from wtforms.validators import Length, NumberRange, DataRequired


class SearchForm(Form):
    keyword = StringField(validators=[Length(min=1, max=30), DataRequired()])
    page = IntegerField(default=1, validators=[NumberRange(min=1, max=99)])
