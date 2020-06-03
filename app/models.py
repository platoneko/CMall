from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
import datetime


class Customer(db.Model):
    __tablename__ = 'Customer'
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(10))
    tel = db.Column(db.String(11))
    pwd = db.Column(db.String(128))

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def set_pwd(self, password):
        self.pwd = generate_password_hash(password)

    def check_pwd(self, password):
        return check_password_hash(self.pwd, password)
    
    @property
    def privilege(self):
        return 0


class Admin(db.Model):
    __tablename__ = 'Admin'
    id = db.Column(db.String(8), primary_key=True)
    pwd = db.Column(db.String(128))
    privilege = db.Column(db.SmallInteger)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def check_pwd(self, password):
        return check_password_hash(self.pwd, password)


@login.user_loader
def load_user(id):
    if session['is_admin']:
        return Admin.query.get(id)
    return Customer.query.get(id)


class ShipAddr(db.Model):
    __tablename__ = 'ShipAddr'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cust_id = db.Column(db.String(8), db.ForeignKey('Customer.id'), index=True)
    addr = db.Column(db.String(100))


class Category(db.Model):
    __tablename__ = 'Category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), unique=True)

class Brand(db.Model):
    __tablename__ = 'Brand'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), unique=True)


class Goods(db.Model):
    __tablename__ = 'Goods'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))
    detail = db.relationship('GoodsDetail', backref='goods', uselist=False)


class GoodsDetail(db.Model):
    __tablename__ = 'GoodsDetail'
    id = db.Column(db.Integer, db.ForeignKey('Goods.id'), primary_key=True)
    cate_id = db.Column(db.Integer, db.ForeignKey('Category.id'), index=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('Brand.id'), index=True)
    purchase_price = db.Column(db.DECIMAL(8, 2))
    sale_price = db.Column(db.DECIMAL(8, 2))
    stock = db.Column(db.Integer)
    sales_num = db.Column(db.Integer)
    description = db.Column(db.String(500))
    images = db.relationship('Image', backref='goods', lazy='dynamic')


class Image(db.Model):
    __tablename__ = 'Image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(100))
    goods_id = db.Column(db.Integer, db.ForeignKey('GoodsDetail.id'), index=True)


class CustOrder(db.Model):
    __tablename__ = 'CustOrder'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    pay_time = db.Column(db.DateTime)
    goods_id = db.Column(db.Integer, db.ForeignKey('Goods.id'))
    cust_id = db.Column(db.Integer, db.ForeignKey('Customer.id'), index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('Admin.id'), index=True)
    shipaddr_id = db.Column(db.Integer, db.ForeignKey('ShipAddr.id'))
    status = db.Column(db.SmallInteger, default=0)
    quantity = db.Column(db.SmallInteger)
    cost = db.Column(db.DECIMAL(8, 2))