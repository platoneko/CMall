from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import StringField, BooleanField, PasswordField, SubmitField, \
    SelectField, DecimalField, IntegerField, TextAreaField, FileField, Field
from wtforms.validators import DataRequired, EqualTo, Regexp, Length, NumberRange
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
        return HTMLString(f"<button %s>{field.value}</button>" % (html_params(**kwargs)))


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
    user = StringField('用户名', validators=[
        DataRequired('用户名不能为空'),
        Length(3, 16, message='用户名必须是3~16位数字或字母'),
        Regexp(PASSWORD_REG, message='用户名必须是3~16位数字或字母')])
    password = PasswordField('密码', validators=[
        DataRequired('密码不能为空'),
        Length(8, 16, message='密码必须是8~16位数字或字母'),
        Regexp(PASSWORD_REG, message='密码必须是8~16位数字或字母')])
    repassword = PasswordField('重复输入密码', validators=[EqualTo('password', '两次输入密码不一致')])
    tel = StringField('手机号码', validators=[
        DataRequired('手机号码不能为空'),
        Regexp(TEL_REG, message='请输入正确的手机号码')])
    name = StringField('昵称', validators=[
        DataRequired('昵称不能为空'),
        Length(1, 10, message='昵称必须是1~10位中文字符、数字或字母'),
        Regexp(PASSWORD_REG, message='昵称必须是1~10位中文字符、数字或字母')])
    submit = SubmitField('确认注册')


class ValidationForm(FlaskForm):
    password = PasswordField('密码', validators=[DataRequired('密码不能为空')])
    submit = SubmitField('提交')


class CateForm(FlaskForm):
    name = StringField('类别名', validators=[
        DataRequired('类别名不能为空'),
        Length(1, 20, message='类别名长度不得超过20个字符')])
    submit = SubmitField('添加')


class BrandForm(FlaskForm):
    name = StringField('品牌名', validators=[
        DataRequired('品牌名不能为空'),
        Length(1, 20, message='品牌名长度不得超过20个字符')])
    submit = SubmitField('添加')


class AddGoodsForm(FlaskForm):
    name = StringField('商品名', validators=[
        DataRequired('商品名不能为空'),
        Length(1, 30, message='商品名长度不得超过30个字符')])
    cate = SelectField('商品类别', validators=[DataRequired('类别不能为空')], coerce=int)
    brand = SelectField('品牌', validators=[DataRequired('品牌不能为空')], coerce=int)
    purchase_price = DecimalField('进货价', places=2, validators=[
        DataRequired('非法的输入'),
        NumberRange(0.01, 999999.99, message='进货价必须在0.01~999999.99之间')])
    sale_price = DecimalField('售价', places=2, validators=[
        DataRequired('非法的输入'),
        NumberRange(0.01, 999999.99, message='售价必须在0.01~999999.99之间')])
    stock = IntegerField('库存', validators=[
        DataRequired('非法的输入'),
        NumberRange(1, 100000, message='库存必须在1~100000之间')])
    description = TextAreaField('描述', validators=[
        DataRequired('描述不能为空'),
        Length(10, 500, message='描述长度不得少于10个字符、不得超过500个字符')])
    cover = FileField('上传商品封面图片', validators=[
        FileRequired('商品必须有封面图片'),
        FileAllowed(['jpg'], '仅支持.jpg后缀的图片文件')])
    images = FileField('上传商品展示图片', validators=[
        FileAllowed(['jpg'], '仅支持.jpg后缀的图片文件')])
    submit = SubmitField('提交')


class EditGoodsForm(FlaskForm):
    name = StringField('商品名', validators=[
        DataRequired('商品名不能为空'),
        Length(1, 30, message='商品名长度不得超过30个字符')])
    purchase_price = DecimalField('进货价', places=2, validators=[
        DataRequired('非法的输入'),
        NumberRange(0.01, 999999.99, message='进货价必须在0.01~999999.99之间')])
    sale_price = DecimalField('售价', places=2, validators=[
        DataRequired('非法的输入'),
        NumberRange(0.01, 999999.99, message='售价必须在0.01~999999.99之间')])
    stock = IntegerField('库存', validators=[
        DataRequired('非法的输入'),
        NumberRange(1, 100000, message='库存必须在1~100000之间')])
    description = TextAreaField('描述', validators=[
        DataRequired('描述不能为空'),
        Length(10, 500, message='描述长度不得少于10个字符、不得超过500个字符')])
    submit = SubmitField('提交')


class EditCoverForm(FlaskForm):
    cover = FileField('上传商品封面图片', validators=[
        FileRequired('商品必须有封面图片'),
        FileAllowed(['jpg'], '仅支持.jpg后缀的图片文件')])
    submit = SubmitField('更换封面')


class EditImageForm(FlaskForm):
    images = FileField('上传商品展示图片', validators=[
        FileAllowed(['jpg'], '仅支持.jpg后缀的图片文件')])
    submit = SubmitField('添加/删除图片')


class AddrForm(FlaskForm):
    addr = StringField('详细地址', validators=[
        DataRequired('详细地址不能为空'),
        Length(1, 80, message='地址长度不得超过80个字符')])
    submit = SubmitField('提交')


class PurchaseForm(FlaskForm):
    qty = IntegerField('购买数量', default=1, validators=[
        DataRequired('非法的输入'),
        NumberRange(1, 99, '一次性购买数量不能超过99')])
    addr = SelectField('收货地址', validators=[DataRequired('地址不能为空')], coerce=int)
    submit = SubmitField('提交订单')


class AppraisalForm(FlaskForm):
    score = SelectField(
        '总体评分',
        validators=[DataRequired('评分不能为空')],
        choices=[(1, '很差'), (2, '较差'), (3, '一般'), (4, '推荐'), (5, '力荐')],
        coerce=int,
        default=4)
    content = TextAreaField('内容', validators=[Length(0, 100, message='评价内容不得超过100个字符')])
    submit = SubmitField('发表评价')


class AdminRegisterForm(FlaskForm):
    user = StringField('用户名', validators=[
        DataRequired('用户名不能为空'),
        Length(3, 16, message='用户名必须是3~16位数字或字母'),
        Regexp(PASSWORD_REG, message='用户名必须是3~16位数字或字母')])
    password = PasswordField('密码', validators=[
        DataRequired('密码不能为空'),
        Length(8, 16, message='密码必须是8~16位数字或字母'),
        Regexp(PASSWORD_REG, message='密码必须是8~16位数字或字母')])
    repassword = PasswordField('重复输入密码', validators=[EqualTo('password', '两次输入密码不一致')])
    privilege = IntegerField('权限', default=50, validators=[
        DataRequired('非法的输入'),
        NumberRange(1, 100, '请输入1~100的整数')])
    submit = SubmitField('确认注册')


class InventoryForm(FlaskForm):
    stock = IntegerField('实际库存', validators=[
        DataRequired('非法的输入'),
        NumberRange(1, 100000, message='库存必须在1~100000之间')])
    submit = SubmitField('提交')
