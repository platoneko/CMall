from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session


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


class Category(db.Model):
    __tablename__ = 'Category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))

class Brand(db.Model):
    __tablename__ = 'Brand'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))


class Goods(db.Model):
    __tablename__ = 'Goods'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))
    cate_id = db.Column(db.Integer, db.ForeignKey('Category.id'))
    brand_id = db.Column(db.Integer, db.ForeignKey('Brand.id'))
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
    goods_id = db.Column(db.Integer, db.ForeignKey('Goods.id'))

