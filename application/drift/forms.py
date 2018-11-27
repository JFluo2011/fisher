from wtforms import StringField, Form
from wtforms.validators import Length, DataRequired, Regexp


class DriftForm(Form):
    recipient_name = StringField(
        '收件人姓名', validators=[Length(min=2, max=20, message='收件人姓名长度必须在2-20之间'), DataRequired()])
    mobile = StringField('手机号', validators=[Regexp('^1[0-9]{10}$', 0, '请输入正确的手机号'), DataRequired()])
    message = StringField('留言')
    address = StringField(
        '邮寄地址', validators=[Length(min=10, max=70, message='地址还不到10个字？请尽量填写详细地址'), DataRequired()])

