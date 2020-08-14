from datetime import datetime
from getirwapp import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

my_bucket = db.Table('bucket', db.Column(('user_id'), db.Integer, db.ForeignKey('user.id'), primary_key=True),
                               db.Column(('prod_id'), db.Integer, db.ForeignKey('product.product_id'), primary_key=True))

my_order = db.Table('orders', db.Column(('user_id'), db.Integer, db.ForeignKey('user.id'), primary_key=True),
                              db.Column(('prod_id'), db.Integer, db.ForeignKey('product.product_id'), primary_key=True))


class OrderInfo(db.Model, UserMixin):
    order_id = db.Column(db.Integer,  primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    note = db.Column(db.String(120))
    payment = db.Column(db.String(20), default="Cash", nullable=False)
    quantity = db.Column(db.Integer, default=1)
    discount = db.Column(db.Integer)
    order_amount = db.Column(db.Integer)
    plastic_tools = db.Column(db.String)

class SubOrder(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    prod_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), primary_key=True)
    amount = db.Column(db.Integer)
    price = db.Column(db.Integer)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    tel_no = db.Column(db.String(11), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    in_bucket = db.relationship('Product', secondary=my_bucket, backref=db.backref('user_buckets', lazy='dynamic'))
    in_order = db.relationship('Product', secondary=my_order, backref=db.backref('user_orders', lazy='dynamic'))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}', '{self.tel_no}', '{self.address}')"


class Product(db.Model, UserMixin):
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(30), unique=True, nullable=False)
    product_price = db.Column(db.Integer, nullable=False)
    product_amount = db.Column(db.Integer, nullable=False)
    product_category = db.Column(db.String(30), nullable=False)
    product_def = db.Column(db.String(50))

    def __repr__(self):
        return f"Product('{self.product_name}', '{self.product_price}', '{self.product_amount}', '{self.product_category}', '{self.product_def}')"

class Promotion(db.Model, UserMixin):
    promotion_id = db.Column(db.Integer, primary_key=True)
    promotion_heading = db.Column(db.String(120), nullable=False)
    promotion_def = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"Promotion('{self.promotion_heading}', '{self.promotion_def}')"


