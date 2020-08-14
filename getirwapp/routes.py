from flask import render_template, flash, redirect, url_for, request, jsonify
from getirwapp import app, db, bcrypt
from getirwapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, SearchForm, OrderForm
from getirwapp.models import User, Product, my_bucket, SubOrder, OrderInfo
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/home")
@app.route("/")
def home():
    return render_template('home.html')


@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, tel_no=form.tel_no.data, address=form.address.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You can now Login!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET','POST'] )
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful! Please check your email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.tel_no = form.tel_no.data
        current_user.address = form.address.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.tel_no.data = current_user.tel_no
        form.address.data = current_user.address
    image_file = url_for('static', filename='profile_pics/default.jpg')
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    #form.category.choices = [ (product.product_category) for product in Product.query.distinct() ]
    #print(form.category.choices)

    query = db.session.query(Product.product_category.distinct().label("product_category"))
    form.category.choices = [ (product.product_category) for product in query.all()]

    bucket_pressed = False
    total_price=0
    if request.method == 'POST':
        selected_category = form.category.data
        selected_product = Product.query.filter_by(product_id=form.product.data).first()
        selected_product_name = selected_product.product_name
        selected_amount = form.amount.data
        #res = db.engine.execute('SELECT product_name FROM product WHERE product_id=1')
        # names = [row[0] for row in res]
        # print(names)
        # print(selected_category)
        # #print(selected_product)
        # print(selected_product_name)
        # print(selected_amount)

        selected_product.user_buckets.append(current_user)
        price = int(selected_amount) * selected_product.product_price
        sub = SubOrder(user_id=current_user.id, prod_id=selected_product.product_id, amount=selected_amount, price=price)
        db.session.add(sub)
        db.session.commit()
        bucket_pressed = True


    return render_template('search.html', title='Search', form=form, bucket_pressed=bucket_pressed)

@app.route('/product/<get_product>')
def prod(get_product):
    product_data = Product.query.filter_by(product_category=get_product).all()
    prodArray = []
    for product in product_data:
        prodObj = {}
        prodObj['id'] = product.product_id
        prodObj['name'] = product.product_name
        prodArray.append(prodObj)
    return jsonify({'prodlist' : prodArray})

@app.route('/mybucket', methods=['GET', 'POST'])
@login_required
def mybucket():
    form = OrderForm()
    amount_sub = []
    price_sub = []
    prod_names=[]
    prod_ids = []

    for product in current_user.in_bucket:
        prod_names.append(product.product_name)
    for product in current_user.in_bucket:
        prod_ids.append(product.product_id)

    a=[]
    for id in prod_ids:
        a = SubOrder.query.filter_by(prod_id=id).first()
        amount_sub.append(a.amount)

    p = []
    for id in prod_ids:
        p = SubOrder.query.filter_by(prod_id=id).first()
        price_sub.append(p.price)

    total_price = 0
    for i in range(len(price_sub)):
        total_price = total_price + price_sub[i]

    if request.method == 'POST':
        order = OrderInfo(user_id=current_user.id, note=form.note.data, payment=form.payment.data,order_amount=total_price)
        db.session.add(order)
        current_user.in_bucket[:]=[]
        SubOrder.query.delete()
        db.session.commit()

    return render_template('mybucket.html', title='Bucket', prod_names=prod_names, amount_sub=amount_sub, price_sub=price_sub, total_price=total_price, form=form)


@app.route('/payments', methods=['GET', 'POST'])
@login_required
def payments():
   p = []
   m = []
   for x in OrderInfo.query.filter_by(user_id=current_user.id):
       p.append(x.order_amount)
       m.append(x.payment)
   return render_template('payments.html', title='Payments', p=p, m=m)