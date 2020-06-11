import os
import datetime
from flask import render_template, redirect, request, flash, g, session, abort, url_for
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from .forms import LoginForm, RegisterForm, AddGoodsForm, CateForm, BrandForm, \
    ValidationForm, AddrForm, PurchaseForm, AppraisalForm, AdminRegisterForm, \
    InventoryForm, EditGoodsForm, EditCoverForm, EditImageForm, EditCustForm, \
    EditPasswordForm
from .models import Customer, Admin, Category, Brand, Goods, GoodsDetail, \
    Image, ShipAddr, CustOrder, Appraisal, Inventory, Cover
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


@app.route('/cate/index/<id>')
def cate(id):
    cate = Category.query.get_or_404(id)
    goods_list = cate.goods
    return render_template('/cate/index.html', name=cate.name, goods_list=goods_list, next=f'/cate/index/{id}')


@app.route('/brand/index/<id>')
def brand(id):
    brand = Brand.query.get_or_404(id)
    goods_list = brand.goods
    return render_template('/brand/index.html', name=brand.name, goods_list=goods_list, next=f'/brand/index/{id}')


@app.route('/goods/index/<id>', methods=['GET', 'POST'])
def goods(id):
    goods = GoodsDetail.query.get_or_404(id)
    cate_name = goods.cate.name
    brand_name = goods.brand.name
    sql = f"""
        SELECT Customer.name, score, Appraisal.create_time, content
        FROM CustOrder, Appraisal, Customer
        WHERE (goods_id = {id} AND
          CustOrder.id = Appraisal.order_id AND
          Customer.id = CustOrder.cust_id)
    """
    result_list = db.session.execute(sql).fetchall()
    avg_score = 0
    if result_list:
        for result in result_list:
            avg_score += result.score
        avg_score = round(avg_score/len(result_list), 1)
    return render_template(
        '/goods/index.html',
        goods=goods,
        cate_name=cate_name,
        brand_name=brand_name,
        score=avg_score,
        result_list=result_list,
        next=f'/goods/index/{id}')


@app.route('/auth/login', methods=['GET', 'POST'])
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
            return redirect('/auth/login')
        if not user.check_pwd(form.password.data):
            flash('密码错误')
            return redirect('/auth/login')
        if form.is_admin.data:
            session['is_admin'] = True
        else:
            session['is_admin'] = False
        login_user(user, remember=False)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = '/index'
        return redirect(next_page)
    return render_template('/auth/login.html', form=form)


@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    if g.user.is_authenticated:
        return redirect('/index')
    form = RegisterForm()
    if form.validate_on_submit():
        if Customer.query.get(form.user.data):
            flash('该用户名已被注册')
            return redirect('/auth/register')
        user = Customer(id=form.user.data, name=form.name.data, tel=form.tel.data)
        user.set_pwd(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功')
        next_page = request.args.get('next')
        return redirect(url_for('login', next=next_page))
    return render_template('/auth/register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/index')


@app.route('/goods/add', methods=['GET', 'POST'])
@login_required
def goods_add():
    if g.user.privilege < 100:
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
        goods = Goods(name=form.name.data)
        db.session.add(goods)
        goods_detail = GoodsDetail(
            goods=goods,
            cate_id=form.cate.data,
            brand_id=form.brand.data,
            purchase_price=form.purchase_price.data,
            sale_price=form.sale_price.data,
            stock=form.stock.data,
            real_stock=form.stock.data,
            sales_num=0,
            description=form.description.data)
        db.session.add(goods_detail)
        f = form.cover.data
        filename = random_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        url = os.path.join('/images/goods', filename)
        cover = Cover(url=url, goods=goods_detail)
        db.session.add(cover)
        files = request.files.getlist('images')
        for f in files:
            if f.filename == '':
                break
            filename = random_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            url = os.path.join('/images/goods', filename)
            image = Image(url=url, goods=goods_detail)
            db.session.add(image)
        db.session.commit()
        flash('商品添加成功')
        return redirect('/goods/add')
    return render_template('/goods/add.html', form=form)


@app.route('/goods/edit/<id>')
@login_required
def goods_edit(id):
    if g.user.privilege < 100:
        abort(403)
    goods = GoodsDetail.query.get_or_404(id)
    goods_form = EditGoodsForm()
    cover_form = EditCoverForm()
    image_form = EditImageForm()
    return render_template(
        'goods/edit.html',
        goods_form=goods_form,
        cover_form=cover_form,
        image_form=image_form,
        goods=goods,
        cover=goods.cover,
        images=goods.images)


@app.route('/goods/edit/info/<id>', methods=['POST'])
@login_required
def goods_edit_info(id):
    if g.user.privilege < 100:
        abort(403)
    goods = GoodsDetail.query.get_or_404(id)
    goods_form = EditGoodsForm()
    cover_form = EditCoverForm()
    image_form = EditImageForm()
    if goods_form.validate_on_submit():
        goods = db.session.query(GoodsDetail).with_for_update().get(id)
        goods.goods.name = goods_form.name.data
        goods.purchase_price = goods_form.purchase_price.data
        goods.sale_price = goods_form.sale_price.data
        goods.real_stock = goods_form.stock.data
        sql = f"""
            SELECT SUM(quantity) FROM CustOrder
            WHERE (
              goods_id = {goods.id} AND
              status = 1
            )
        """
        sold_qty = db.session.execute(sql).fetchall()[0][0]
        if sold_qty is None:
            sold_qty = 0
        goods.stock = goods_form.stock.data - sold_qty
        goods.description = goods_form.description.data
        db.session.commit()
        return redirect(f'/goods/edit/{id}')
    return render_template(
        'goods/edit.html',
        goods_form=goods_form,
        cover_form=cover_form,
        image_form=image_form,
        goods=goods,
        cover=goods.cover,
        images=goods.images.all())


@app.route('/goods/edit/cover/<id>', methods=['POST'])
@login_required
def goods_edit_cover(id):
    if g.user.privilege < 100:
        abort(403)
    goods = GoodsDetail.query.get_or_404(id)
    goods_form = EditGoodsForm()
    cover_form = EditCoverForm()
    image_form = EditImageForm()
    goods_cover = goods.cover
    if cover_form.validate_on_submit():
        os.remove(os.path.join(app.config['UPLOAD_PATH'], os.path.split(goods_cover.url)[-1]))
        db.session.delete(goods_cover)
        f = cover_form.cover.data
        filename = random_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        url = os.path.join('/images/goods', filename)
        cover = Cover(url=url, goods=goods)
        db.session.add(cover)
        db.session.commit()
        return redirect(f'/goods/edit/{id}')
    return render_template(
        'goods/edit.html',
        goods_form=goods_form,
        cover_form=cover_form,
        image_form=image_form,
        goods=goods,
        cover=goods_cover,
        images=goods.images.all())


@app.route('/goods/edit/images/<id>', methods=['POST'])
@login_required
def goods_edit_images(id):
    if g.user.privilege < 100:
        abort(403)
    goods = GoodsDetail.query.get_or_404(id)
    goods_form = EditGoodsForm()
    cover_form = EditCoverForm()
    image_form = EditImageForm()
    images = goods.images.all()
    if image_form.validate_on_submit():
        for img in images:
            if request.form.get(f'img_{img.id}'):
                os.remove(os.path.join(app.config['UPLOAD_PATH'], os.path.split(img.url)[-1]))
                db.session.delete(img)
        files = request.files.getlist('images')
        for f in files:
            if f.filename == '':
                break
            filename = random_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            url = os.path.join('/images/goods', filename)
            image = Image(url=url, goods=goods)
            db.session.add(image)
        db.session.commit()
        return redirect(f'/goods/edit/{id}')
    return render_template(
        'goods/edit.html',
        goods_form=goods_form,
        cover_form=cover_form,
        image_form=image_form,
        goods=goods,
        cover=goods.cover,
        images=images)


@app.route('/cate/edit', methods=['GET', 'POST'])
@login_required
def cate_edit():
    if g.user.privilege < 100:
        abort(403)
    form = CateForm()
    if form.validate_on_submit():
        if Category.query.filter_by(name=form.name.data).first():
            flash(f'类别\"{form.name.data}\"已存在')
            return redirect('/cate/edit')
        else:
            db.session.add(Category(name=form.name.data))
            db.session.commit()
            flash('添加成功')
            return redirect('/cate/edit')
    categories = Category.query.all()
    return render_template('/cate/edit.html', form=form, categories=categories)


@app.route('/brand/edit', methods=['GET', 'POST'])
@login_required
def brand_edit():
    if g.user.privilege < 100:
        abort(403)
    form = BrandForm()
    if form.validate_on_submit():
        if Brand.query.filter_by(name=form.name.data).first():
            flash(f'品牌\"{form.name.data}\"已存在')
            return redirect('/brand/edit')
        else:
            db.session.add(Brand(name=form.name.data))
            db.session.commit()
            flash('添加成功')
            return redirect('/brand/edit')
    brands = Brand.query.all()
    return render_template('/brand/edit.html', form=form, brands=brands)


@app.route('/cate/delete/<id>', methods=['GET', 'POST'])
@login_required
def cate_delete(id):
    if g.user.privilege < 100:
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
            return redirect('/cate/edit')
        else:
            flash('身份验证失败')
            return redirect('/cate/edit')
    return render_template('/auth/validation.html', msg=f'正在删除类别\"{cate.name}\"', form=form)


@app.route('/brand/delete/<id>', methods=['GET', 'POST'])
@login_required
def brand_delete(id):
    if g.user.privilege < 100:
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
            return redirect('/brand/edit')
        else:
            flash('身份验证失败')
            return redirect('/brand/edit')
    return render_template('/auth/validation.html', msg=f'正在删除品牌\"{brand.name}\"', form=form)


@app.route('/goods/delete/<id>', methods=['GET', 'POST'])
@login_required
def goods_delete(id):
    if g.user.privilege < 100:
        abort(403)
    goods = GoodsDetail.query.get_or_404(id)
    form = ValidationForm()
    name = goods.goods.name
    if form.validate_on_submit():
        if g.user.check_pwd(form.password.data):
            for image in goods.images.all():
                os.remove(os.path.join(app.config['UPLOAD_PATH'], os.path.split(image.url)[-1]))
            os.remove(os.path.join(app.config['UPLOAD_PATH'], os.path.split(goods.cover.url)[-1]))
            db.session.delete(goods)
            db.session.commit()
            flash(f'商品\"{name}\"已被删除')
            return redirect('/index')
        else:
            flash('身份验证失败')
            return redirect('/index')
    return render_template('/auth/validation.html', msg=f'正在删除商品\"{name}\"', form=form)


@app.route('/cust/addr', methods=['GET', 'POST'])
@login_required
def cust_addr():
    if g.user.privilege:
        return redirect('/index')
    form = AddrForm()
    if form.validate_on_submit():
        province = request.form.get('province')
        city = request.form.get('city')
        if not province or not city:
            flash('省份或城市不能为空')
            return redirect('/cust/addr')
        db.session.add(ShipAddr(cust_id=g.user.id, addr=('').join([province, city, form.addr.data])))
        db.session.commit()
        flash('添加成功')
        return redirect('/cust/addr')
    addrs = g.user.addrs
    return render_template('/cust/addr.html', addrs=addrs, form=form)


@app.route('/cust/addr/delete/<id>')
@login_required
def addr_delete(id):
    if g.user.privilege:
        return redirect('/index')
    addr = ShipAddr.query.get(id)
    if addr.cust_id != g.user.id:
        abort(403)
    addr.cust_id = None
    db.session.commit()
    flash('地址删除成功')
    return redirect('/cust/addr')


@app.route('/cust/purchase/<id>', methods=['GET', 'POST'])
@login_required
def purchase(id):
    if g.user.privilege:
        return redirect('/index')
    addrs = g.user.addrs
    if not addrs:
        return redirect('/cust/addr')
    goods = GoodsDetail.query.get_or_404(id)
    if goods.stock == 0:
        flash('商品库存不足')
        return redirect(f'/goods/index/{id}')
    form = PurchaseForm()
    addr_choices = []
    for addr in addrs:
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
        return redirect(f'/cust/payment/{order.id}')
    return render_template('/cust/purchase.html', form=form, goods=goods)


@app.route('/cust/payment/<id>')
@login_required
def payment(id):
    if g.user.privilege:
        return redirect('/index')
    order = CustOrder.query.get_or_404(id)
    if order.cust_id != g.user.id:
        abort(403)
    if order.goods.detail is None:
        flash('商品已下架，订单取消')
        return redirect(f'/cust/order/delete/{order.id}')
    return render_template('/cust/payment.html', order=order)


@app.route('/cust/paying/<id>')
@login_required
def paying(id):
    if g.user.privilege:
        return redirect('/index')
    order = CustOrder.query.get_or_404(id)
    if order.status != 0:
        abort(404)
    goods = db.session.query(GoodsDetail).with_for_update().get(order.goods_id)
    if goods is None:
        db.session.commit()
        flash('商品已下架，订单取消')
        return redirect(f'/cust/order/delete/{order.id}')
    if goods.stock < order.quantity:
        db.session.commit()
        flash('商品库存不足')
        return redirect('/cust/orders/0')
    goods.stock -= order.quantity
    goods.sales_num += order.quantity
    order.pay_time = datetime.datetime.now()
    order.status = 1
    db.session.commit()
    flash('支付成功')
    return redirect('/cust/orders/1')


@app.route('/cust/orders/<status>')
@login_required
def cust_orders(status):
    if g.user.privilege:
        return redirect('/index')
    status = int(status)
    if status < 0 or status > 4:
        abort(404)
    msg = [
        '未付款订单',
        '待发货订单',
        '待签收订单',
        '待评价订单',
        '已完成订单'
    ]
    orders = CustOrder.query.filter_by(cust_id=g.user.id, status=status). \
        order_by(CustOrder.id.desc()).all()
    return render_template('/cust/orders.html', orders=orders, msg=msg[status])


@app.route('/cust/order/<id>')
@login_required
def cust_order(id):
    if g.user.privilege:
        return redirect('/index')
    order = CustOrder.query.get_or_404(id)
    if order.cust_id != g.user.id:
        abort(403)
    status = [
        '未付款',
        '待发货',
        '待签收',
        '待评价',
        '已完成'
    ]
    appraisal = order.appraisal
    return render_template('cust/order.html', order=order, status=status[order.status], appraisal=appraisal)


@app.route('/cust/order/delete/<id>')
@login_required
def order_delete(id):
    if g.user.privilege:
        return redirect('/index')
    order = CustOrder.query.get_or_404(id)
    if order.cust_id != g.user.id:
        abort(403)
    if order.status != 0:
        abort(404)
    db.session.delete(order)
    db.session.commit()
    flash('订单已取消')
    return redirect(f'/cust/orders/0')


@app.route('/cust/signed/<id>')
@login_required
def signed(id):
    if g.user.privilege:
        return redirect('/index')
    order = CustOrder.query.get_or_404(id)
    if order.cust_id != g.user.id:
        abort(403)
    if order.status != 2:
        abort(404)
    order.status = 3
    db.session.commit()
    return redirect(f'/cust/orders/3')


@app.route('/cust/appraisal/<id>', methods=['GET', 'POST'])
@login_required
def appraisal(id):
    if g.user.privilege:
        redirect('/index')
    order = db.session.query(CustOrder).with_for_update().get(id)
    if order.goods.detail is None:
        order.status = 4
        db.session.commit()
        flash('商品已下架，订单完成')
        return redirect('/cust/orders/4')
    if order.status == 4:
        db.session.commit()
        flash('订单已完成，请勿重复发表评价')
        return redirect('/cust/orders/4')
    if order.status != 3:
        db.session.commit()
        abort(404)
    form = AppraisalForm()
    if form.validate_on_submit():
        appraisal = Appraisal(
            score=form.score.data,
            order_id=id,
            content=form.content.data)
        db.session.add(appraisal)
        order.status = 4
        db.session.commit()
        flash('评价提交成功，订单完成')
        return redirect('/cust/orders/4')
    db.session.commit()
    return render_template('cust/appraisal.html', form=form)


@app.route('/admin/orders/<status>')
@login_required
def admin_orders(status):
    status = int(status)
    if status < 0 or status > 4:
        abort(404)
    msg = [
        '待处理订单',
        '待发货订单',
        '待签收订单',
        '待评价订单',
        '已完成订单'
    ]
    if status == 0:
        orders = CustOrder.query.filter_by(admin_id=None, status=1). \
            order_by(CustOrder.id.desc()).all()
    else:
        orders = CustOrder.query.filter_by(admin_id=g.user.id, status=status). \
            order_by(CustOrder.id.desc()).all()
    return render_template('admin/orders.html', orders=orders, msg=msg[status])


@app.route('/admin/order/<id>')
@login_required
def admin_order(id):
    if g.user.privilege < 50:
        abort(403)
    order = CustOrder.query.get_or_404(id)
    if order.admin_id and order.admin_id != g.user.id:
        abort(403)
    if order.admin_id is None:
        status = 0
    else:
        status = order.status
    appraisal = order.appraisal
    goods = order.goods
    if order.status == 1:
        stock = goods.detail.real_stock
    else:
        stock = None
    return render_template('admin/order.html', order=order, status=status, appraisal=appraisal, name=goods.name, stock=stock)


@app.route('/admin/order/manage/<id>')
@login_required
def admin_order_manage(id):
    if g.user.privilege < 50:
        abort(403)
    order = db.session.query(CustOrder).with_for_update().get(id)
    if order is None:
        db.session.commit()
        abort(404)
    if order.admin_id is not None:
        db.session.commit()
        flash('订单已经有管理员处理')
        return redirect('/admin/orders/0')
    order.admin_id = g.user.id
    db.session.commit()
    return redirect('/admin/orders/1')


@app.route('/admin/ship/<id>')
@login_required
def admin_ship(id):
    if g.user.privilege < 50:
        abort(403)
    order = CustOrder.query.get_or_404(id)
    if order.admin_id != g.user.id:
        abort(403)
    if order.status != 1:
        abort(404)
    order.status = 2
    order.goods.detail.real_stock -= order.quantity
    db.session.commit()
    return redirect('/admin/orders/2')


@app.route('/admin/register', methods=['GET', 'POST'])
@login_required
def admin_register():
    if g.user.privilege < 100:
        abort(403)
    form = AdminRegisterForm()
    if form.validate_on_submit():
        if Admin.query.get(form.user.data):
            flash('该用户名已被注册')
            return redirect('/admin/register')
        user = Admin(id=form.user.data, privilege=form.privilege.data)
        user.set_pwd(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功')
        return redirect('/index')
    return render_template('admin/register.html', form=form)


@app.route('/goods/invent/<id>', methods=['GET', 'POST'])
@login_required
def goods_invent(id):
    if g.user.privilege < 50:
        abort(403)
    goods = GoodsDetail.query.get_or_404(id)
    form = InventoryForm()
    if form.validate_on_submit():
        inventory = Inventory(
            goods_id=id,
            admin_id=g.user.id,
            goods_stock=goods.real_stock,
            stock=form.stock.data
        )
        db.session.add(inventory)
        db.session.commit()
        return redirect('/admin/inventory')
    return render_template('goods/invent.html', form=form, goods=goods)


@app.route('/admin/inventory')
@login_required
def inventory():
    if g.user.privilege < 50:
        abort(403)
    inventories = Inventory.query.order_by(Inventory.id.desc()).all()
    return render_template('admin/inventory.html', inventories=inventories)


@app.route('/cust/edit', methods=['GET', 'POST'])
@login_required
def cust_edit():
    if g.user.privilege:
        return redirect('/index')
    form = EditCustForm()
    if form.validate_on_submit():
        g.user.name = form.name.data
        g.user.tel = form.tel.data
        db.session.commit()
        flash('信息更新成功')
        return redirect('/cust/edit')
    return render_template('cust/edit.html', form=form)


@app.route('/password/edit', methods=['GET', 'POST'])
@login_required
def edit_password():
    form = EditPasswordForm()
    if form.validate_on_submit():
        if not g.user.check_pwd(form.old.data):
            flash('密码验证错误')
            return redirect('/password/edit')
        g.user.set_pwd(form.new.data)
        db.session.commit()
        flash('密码修改成功')
        return redirect('/index')
    return render_template('password_edit.html', form=form)


@app.route('/query')
def query():
    inputs = request.args.get('inputs')
    if inputs is None:
        return redirect('/index')
    inputs = inputs.strip()
    if not inputs:
        return redirect('/index')
    key_words = '%'.join(inputs.split())
    goods_list = Goods.query.filter(Goods.name.like(f'%{key_words}%')).all()
    return render_template('/query.html', inputs=inputs, goods_list=goods_list)
