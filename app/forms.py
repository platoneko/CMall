from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, Field
from wtforms.validators import DataRequired, EqualTo, Regexp, Length
from wtforms.widgets import HTMLString, html_params
import re


TEL_REG = re.compile(r'^1(30|31|32|33|34|35|36|37|38|39|50|51|52|53|55|56|57|58|59|80|86|87|88|89)\d{8}$')
PASSWORD_REG = re.compile(r'^\w+$')
USER_REG = re.compile(r'^\w+$')
NAME_REG = re.compile(r'^[\u4e00-\u9fa50-9a-zA-Z_]+$')


class ButtonWidget(object):
	def __call__(self, field, **kwargs):
		if field.name is not None:
			kwargs.setdefault("name", field.name)			
		kwargs.setdefault("type", field.btype)
		kwargs.setdefault('id', field.id)
		return HTMLString(f"<button %s>{field.value}</button>"%(html_params(**kwargs)))


class ButtonField(Field):
	widget = ButtonWidget()
	def __init__(self, value="button", text="button", btype="submit", **kwargs):
		super(ButtonField, self).__init__(**kwargs)
		self.type = "SubmitField"
		self.btype = btype
		self.value = value
		self.text = text


class LoginForm(FlaskForm):
    user = StringField('用户名', validators=[DataRequired('用户名不能为空')])
    password = PasswordField('密码', validators=[DataRequired('密码不能为空')])
    submit = SubmitField('登录')
	is_admin = BooleanField('管理员登录')


class RegisterForm(FlaskForm):
    user = StringField('用户名', validators=[DataRequired('用户名不能为空'), 
		Length(3, 8, message='用户名必须是3-8位数字或字母'), 
		Regexp(PASSWORD_REG, message='用户名必须是3-8位数字或字母')])
    password = PasswordField('密码', validators=[DataRequired('密码不能为空'), 
		Length(8, 16, message='密码必须是8-16位数字或字母'),
		Regexp(PASSWORD_REG, message='密码必须是8-16位数字或字母')])
    repassword = PasswordField('重复输入密码', validators=[EqualTo('password', '两次输入密码不一致')])
    tel = StringField('手机号码', validators=[DataRequired('手机号码不能为空'), Regexp(TEL_REG, message='请输入正确的手机号码')])
    name = StringField('昵称', validators=[DataRequired('昵称不能为空'),
		Length(1, 10, message='昵称必须是1-10位中文字符、数字或字母'),
		Regexp(PASSWORD_REG, message='昵称必须是1-10位中文字符、数字或字母')])
    submit = SubmitField('确认注册')


class OrderSubmitForm(FlaskForm):
