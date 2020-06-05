import os
import datetime
from flask import render_template, redirect, request, flash, g, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from .forms import LoginForm, RegisterForm, AddGoodsForm, CateForm, BrandForm, \
    ValidationForm, AddrForm, PurchaseForm
from .models import Customer, Admin, Category, Brand, Goods, GoodsDetail, \
    Image, ShipAddr, CustOrder
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
    cate = Category.query.get_or_404(id)
    goods_list = cate.goods
    return render_template('/cate.html', name=cate.name, goods_list=goods_list)


@app.route('/brand/<id>')
def brand(id):
    brand = Brand.query.get_or_404(id)
    goods_list = brand.goods
    return render_template('/brand.html', name=brand.name, goods_list=goods_list)


@app.route('/goods/<id>', methods=['GET', 'POST'])
def goods(id):
    goods = GoodsDetail.query.get_or_404(id)
    cate_name = goods.cate.name
    brand_name = goods.brand.name
    return render_template('/goods.html', goods=goods, cate_name=cate_name, brand_name=brand_name)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user.is_authenticated:
        return redirect('/index')
    form = LoginForm()
    if form.validate_on_submit():
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
    if form.validate_on_submit():
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
    if form.validate_on_submit():
        img = form.images.data
        filename = random_filename(img.filename)
        url = os.path.join('/images/goods', filename)
        goods = Goods(name=form.name.data)
        db.session.add(goods)
        goods_detail = GoodsDetail(
            goods=goods,
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


@app.route('/edit_cate', methods=['GET', 'POST'])
@login_required
def edit_cate():
    if (g.user.privilege < 100):
        abort(403)
    form = CateForm()
    if form.validate_on_submit():
        if Category.query.filter_by(name=form.name.data).first():
            flash(f'类别\"{form.name.data}\"已存在')
            return redirect('/edit_cate')
        else:
            db.session.add(Category(name=form.name.data))
            db.session.commit()
            flash('添加成功')
            return redirect('/edit_cate')
    categories = Category.query.all()
    return render_template('/edit_cate.html', form=form, categories=categories)


@app.route('/edit_brand', methods=['GET', 'POST'])
@login_required
def edit_brand():
    if (g.user.privilege < 100):
        abort(403)
    form = BrandForm()
    if form.validate_on_submit():
        if Brand.query.filter_by(name=form.name.data).first():
            flash(f'品牌\"{form.name.data}\"已存在')
            return redirect('/edit_brand')
        else:
            db.session.add(Brand(name=form.name.data))
            db.session.commit()
            flash('添加成功')
            return redirect('/edit_brand')
    brands = Brand.query.all()
    return render_template('/edit_brand.html', form=form, brands=brands)


@app.route('/del_cate/<id>', methods=['GET', 'POST'])
@login_required
def del_cate(id):
    if (g.user.privilege < 100):
        abort(403)
    cate = Category.query.get_or_404(id)
    form = ValidationForm()
    if form.validate_on_submit():
        if g.user.check_pwd(form.password.data):
            for goods in cate.goods:
                for image in goods.images.all():
                    os.remove(os.path.join(app.config['UPLOAD_PATH'], os.path.split(image.url)[-1]))
            db.session.delete(cate)
            db.session.commit()
            flash(f'类别\"{cate.name}\"已被删除')
            return redirect('/edit_cate')
        else:
            flash('身份验证失败')
            return redirect('/edit_cate')
    return render_template('/validation.html', msg=f'正在删除类别\"{cate.name}\"', form=form)


@app.route('/del_brand/<id>', methods=['GET', 'POST'])
@login_required
def del_brand(id):
    if (g.user.privilege < 100):
        abort(403)
    brand = Brand.query.get_or_404(id)
    form = ValidationForm()
    if form.validate_on_submit():
        if g.user.check_pwd(form.password.data):
            for goods in brand.goods:
                for image in goods.images.all():
                    os.remove(os.path.join(app.config['UPLOAD_PATH'], os.path.split(image.url)[-1]))
            db.session.delete(brand)
            db.session.commit()
            flash(f'品牌\"{brand.name}\"已被删除')
            return redirect('/edit_brand')
        else:
            flash('身份验证失败')
            return redirect('/edit_brand')
    return render_template('/validation.html', msg=f'正在删除品牌\"{brand.name}\"', form=form)


@app.route('/del_goods/<id>', methods=['GET', 'POST'])
@login_required
def del_goods(id):
    if (g.user.privilege < 100):
        abort(403)
    goods = GoodsDetail.query.get_or_404(id)
    form = ValidationForm()
    name = goods.goods.name
    if form.validate_on_submit():
        if g.user.check_pwd(form.password.data):
            for image in goods.images.all():
                os.remove(os.path.join(app.config['UPLOAD_PATH'], os.path.split(image.url)[-1]))
            db.session.delete(goods)
            db.session.commit()
            flash(f'商品\"{name}\"已被删除')
            return redirect('/index')
        else:
            flash('身份验证失败')
            return redirect('/index')
    return render_template('/validation.html', msg=f'正在删除商品\"{name}\"', form=form)


@app.route('/edit_addr', methods=['GET', 'POST'])
@login_required
def edit_addr():
    if (g.user.privilege):
        redirect('/index')
    form = AddrForm()
    if form.validate_on_submit():
        province = request.form.get('province')
        city = request.form.get('city')
        if not province or not city:
            flash('省份或城市不能为空')
            return redirect('/edit_addr')
        db.session.add(ShipAddr(cust_id=g.user.id, addr=('').join([province, city, form.addr.data])))
        db.session.commit()
        flash('添加成功')
        return redirect('/edit_addr')
    addrs = g.user.addrs
    return render_template('/edit_addr.html', addrs=addrs, form=form)


@app.route('/del_addr/<id>')
@login_required
def del_addr(id):
    if (g.user.privilege):
        redirect('/index')
    addr = ShipAddr.query.get(id)
    if addr.cust_id != g.user.id:
        abort(403)
    addr.cust_id = None
    db.session.commit()
    flash('地址删除成功')
    return redirect('/edit_addr')


@app.route('/purchase/<id>', methods=['GET', 'POST'])
@login_required
def purchase(id):
    if (g.user.privilege):
        redirect('/index')
    if g.user.addrs is None:
        redirect('edit_addr')
    goods = GoodsDetail.query.get_or_404(id)
    if goods.stock == 0:
        flash('商品库存不足')
        return redirect(f'/goods/{id}')
    form = PurchaseForm()
    addr_choices = []
    for addr in g.user.addrs:
        addr_choices.append((addr.id, addr.addr))
    form.addr.choices = addr_choices
    if form.validate_on_submit():
        cost = GoodsDetail.query.get(id).sale_price * form.qty.data
        order = CustOrder(
            goods_id=id,
            cust_id=g.user.id,
            shipaddr_id=form.addr.data,
            quantity=form.qty.data,
            cost=cost
        )
        db.session.add(order)
        db.session.commit()
        return redirect(f'/payment/{order.id}')
    return render_template('/purchase.html', form=form, goods=goods)


@app.route('/payment/<id>')
@login_required
def payment(id):
    if (g.user.privilege):
        redirect('/index')
    order = CustOrder.query.get_or_404(id)
    if order.cust_id != g.user.id:
        abort(403)
    return render_template('/payment.html', order=order)


@app.route('/paying/<id>')
@login_required
def paying(id):
    if (g.user.privilege):
        redirect('/index')
    order = CustOrder.query.get_or_404(id)
    if order.status != 0:
        abort(404)
    goods = db.session.query(GoodsDetail).with_for_update().get(order.goods_id)
    if goods.stock < order:
        db.session.commit()
        flash('商品库存不足')
        return redirect('/cust_orders/0')
    goods.stock -= order.quantity
    goods.sales_num += order.quantity
    order.pay_time = datetime.datetime.now()
    order.status = 1
    db.session.commit()
    flash('支付成功')
    return redirect('/cust_orders/1')


@app.route('/cust_orders/<status>')
@login_required
def cust_orders(status):
    if (g.user.privilege):
        redirect('/index')
    msg = [
        '未付款订单',
        '已付款订单',
        '已发货订单',
        '待评价订单',
        '已完成订单'
    ]
    orders = CustOrder.query.filter_by(cust_id=g.user.id, status=status). \
        order_by(CustOrder.create_time.desc()).all()
    return render_template('/cust_orders.html', orders=orders, msg=msg[int(status)])


@app.route('/cust_order/<id>')
@login_required
def cust_order(id):
    if (g.user.privilege):
        redirect('/index')
    order = CustOrder.query.get_or_404(id)
    if order.cust_id != g.user.id:
        abort(403)
    return render_template('cust_order.html', order=order)