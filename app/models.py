from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Customer(db.Model):
    __tablename__ = 'Customer'
    custID = db.Column(db.String(8), primary_key=True)
    custName = db.Column(db.String(10))
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
        return self.custID

    def set_pwd(self, password):
        self.pwd = generate_password_hash(password)

    def check_pwd(self, password):
        return check_password_hash(self.pwd, password)


class Admin(db.Model):
    __tablename__ = 'Admin'
    adminID = db.Column(db.String(8), primary_key=True)
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
        return self.adminID

    def check_pwd(self, password):
        return check_password_hash(self.pwd, password)


@login.user_loader
def load_user(id):
    return Customer.query.get(id)


class Category(db.Model):
    __tablename__ = 'Category'
    cateID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cateName = db.Column(db.String(20))

class Brand(db.Model):
    __tablename__ = 'Brand'
    brandID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    brandName = db.Column(db.String(20))


class Goods(db.Model):
    __tablename__ = 'Goods'
    goodsID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    goodsName = db.Column(db.String(30))
    cateID = db.Column(db.Integer, db.ForeignKey('Category.cateID'))
    brandID = db.Column(db.Integer, db.ForeignKey('Brand.brandID'))
    purchasePrice = db.Column(db.DECIMAL(8, 2))
    salePrice = db.Column(db.DECIMAL(8, 2))
    stock = db.Column(db.Integer)
    salesNum = db.Column(db.Integer)
    description = db.Column(db.String(500))
    images = db.relationship('Image', backref='goods', lazy='dynamic')


class Image(db.Model):
    __tablename__ = 'Image'
    imageID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imageUrl = db.Column(db.String(100))
    goodsID = db.Column(db.Integer, db.ForeignKey('Goods.goodsID'))

