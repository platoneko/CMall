from flask import render_template, redirect, request, flash, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from .forms import LoginForm, RegisterForm
from .models import Customer, Admin, Category, Brand, Goods, Image


@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
@app.route('/index')
def index():
    categories = Category.query.all()
    brands = Brand.query.all()
    return render_template('/index.html', 
        categories=categories,
        brands=brands)


@app.route('/cate/<cateID>')
def cate(cateID):
    cateName = Category.query.get(cateID).cateName
    goods_list = Goods.query.filter_by(cateID=cateID)
    return render_template('/cate.html', cateName=cateName, goods_list=goods_list)


@app.route('/brand/<brandID>')
def brand(brandID):
    brandName = Brand.query.get(brandID).brandName
    goods_list = Goods.query.filter_by(brandID=brandID)
    return render_template('/brand.html', brandName=brandName, goods_list=goods_list)


@app.route('/goods/<goodsID>', methods=['GET', 'POST'])
def goods(goodsID):
    goods = Goods.query.get(goodsID)
    cateName = Category.query.get(goods.cateID).cateName
    brandName = Brand.query.get(goods.brandID).brandName
    return render_template('/goods.html', goods=goods, cateName=cateName, brandName=brandName)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect('/index')
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        if form.is_admin.data:
            user = Admin.query.get(form.user.data)
        else:
            user = Customer.query.get(form.user.data)
        if user is None:
            flash('用户名不存在')
            return redirect('/login')
        if not user.check_pwd(form.password.data):
            flash('密码错误')
            return redirect('/login')
        login_user(user, remember=True)
        if form.is_admin.data:
            is_admin = True
            return redirect('/admin')
        return redirect('/index')
    return render_template('/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user is not None and g.user.is_authenticated:
        return redirect('/index')
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        if Customer.query.get(form.user.data):
            flash('该用户名已被注册')
            return redirect('/register')
        user = Customer(custID=form.user.data, custName=form.name.data, tel=form.tel.data)
        user.set_pwd(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功')
        return redirect('/login')
    return render_template('/register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/index')