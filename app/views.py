import os
from flask import render_template, redirect, request, flash, g, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from .forms import LoginForm, RegisterForm, AddGoodsForm
from .models import Customer, Admin, Category, Brand, Goods, GoodsDetail, Image
from .utils import random_filename


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


@app.route('/cate/<id>')
def cate(id):
    name = Category.query.get(id).name
    goods_list = GoodsDetail.query.filter_by(cate_id=id)
    return render_template('/cate.html', name=name, goods_list=goods_list)


@app.route('/brand/<id>')
def brand(id):
    name = Brand.query.get(id).name
    goods_list = GoodsDetail.query.filter_by(brand_id=id)
    return render_template('/brand.html', name=name, goods_list=goods_list)


@app.route('/goods/<id>', methods=['GET', 'POST'])
def goods(id):
    goods = GoodsDetail.query.get(id)
    cate_name = Category.query.get(goods.cate_id).name
    brand_name = Brand.query.get(goods.brand_id).name
    return render_template('/goods.html', goods=goods, cate_name=cate_name, brand_name=brand_name)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user.is_authenticated:
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
        if form.is_admin.data:
            session['is_admin'] = True
        else:
            session['is_admin'] = False
        login_user(user, remember=False)
        return redirect('/index')
    return render_template('/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user.is_authenticated:
        return redirect('/index')
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        if Customer.query.get(form.user.data):
            flash('该用户名已被注册')
            return redirect('/register')
        user = Customer(id=form.user.data, name=form.name.data, tel=form.tel.data)
        user.set_pwd(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功')
        return redirect('/login')
    return render_template('/register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/index')


@app.route('/add_goods', methods=['GET', 'POST'])
@login_required
def add_goods():
    if (g.user.privilege < 100):
        abort(403)
    form = AddGoodsForm()
    categories = Category.query.all()
    cate_choices = []
    for cate in categories:
        cate_choices.append((cate.id, cate.name))
    form.cate.choices = cate_choices
    brands = Brand.query.all()
    brand_choices = []
    for brand in brands:
        brand_choices.append((brand.id, brand.name))
    form.brand.choices = brand_choices
    if request.method == 'POST' and form.validate_on_submit():
        img = form.images.data
        filename = random_filename(img.filename)
        url = os.path.join('/images/goods', filename)
        goods = Goods(name=form.name.data)
        db.session.add(goods)
        goods_detail = GoodsDetail(goods=goods,
            cate_id=form.cate.data,
            brand_id=form.brand.data,
            purchase_price=form.purchase_price.data,
            sale_price=form.sale_price.data,
            stock=form.stock.data,
            sales_num=0,
            description=form.description.data)
        db.session.add(goods_detail)
        image = Image(url=url, goods=goods_detail)
        db.session.add(image)
        img.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        db.session.commit()
        flash('商品添加成功')
        return redirect('/add_goods')
    return render_template('/add_goods.html', form=form)